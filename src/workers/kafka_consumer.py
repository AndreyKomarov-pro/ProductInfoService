import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from aiokafka.structs import ConsumerRecord
from sqlalchemy.exc import InterfaceError, OperationalError, SQLAlchemyError

from src.config import settings
from src.db import SessionFactory
from src.exceptions import TransientError
from src.infrastructure.kafka.producer import KafkaProducer
from src.repositories.processed_event_repository import ProcessedEventRepository
from src.repositories.product_info_repository import ProductInfoRepository
from src.services.product_info_service import ProductInfoService

logger = logging.getLogger(__name__)


async def consume_events(producer: KafkaProducer) -> None:
    consumer = AIOKafkaConsumer(
        *settings.kafka_topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    logger.info("Kafka consumer started")
    try:
        async for msg in consumer:
            try:
                await _process_message(msg, consumer, producer)
            except KafkaError as exc:
                logger.error("Kafka error: %s", exc)
                await asyncio.sleep(settings.kafka_consumer_retry_delay)
            except Exception as exc:
                logger.exception("Unexpected error: %s", exc)
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def _process_message(
    msg: ConsumerRecord,
    consumer: AIOKafkaConsumer,
    producer: KafkaProducer,
) -> None:
    try:
        envelope = json.loads(msg.value.decode("utf-8"))
        event_id = UUID(envelope["event_id"])
        event_type = envelope["event_type"]
        aggregate_id = UUID(envelope["aggregate_id"])
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("Non-retryable parse error: %s", exc)
        await _send_to_dlq(producer, msg, str(exc), 0)
        await consumer.commit()
        return

    last_exc: Exception | None = None
    for attempt in range(1, settings.kafka_consumer_max_retries + 1):
        try:
            is_new = await _handle_event(
                event_id, msg.topic, event_type, aggregate_id,
            )
            if is_new:
                logger.info(
                    "Processed event %s type=%s from %s",
                    event_id,
                    event_type,
                    msg.topic,
                )
            else:
                logger.debug("Duplicate event %s, skipping", event_id)
            break
        except TransientError as exc:
            last_exc = exc
            logger.warning(
                "Attempt %d/%d failed for event %s: %s",
                attempt,
                settings.kafka_consumer_max_retries,
                event_id,
                exc,
            )
            if attempt < settings.kafka_consumer_max_retries:
                await asyncio.sleep(settings.kafka_consumer_retry_delay)
        except SQLAlchemyError as exc:
            logger.error(
                "Non-retryable database error for event %s: %s", event_id, exc,
            )
            await _send_to_dlq(producer, msg, str(exc), attempt - 1)
            break
    else:
        await _send_to_dlq(
            producer, msg, str(last_exc), settings.kafka_consumer_max_retries,
        )

    await consumer.commit()


async def _handle_event(
    event_id: UUID, topic: str, event_type: str, aggregate_id: UUID,
) -> bool:
    try:
        async with SessionFactory() as session:
            service = ProductInfoService(
                ProductInfoRepository(session),
                ProcessedEventRepository(session),
            )
            is_new = await service.handle_event(
                event_id, topic, event_type, aggregate_id,
            )
            if is_new:
                await session.commit()
            return is_new
    except (OperationalError, InterfaceError) as exc:
        raise TransientError(str(exc)) from exc


async def _send_to_dlq(
    producer: KafkaProducer,
    msg: ConsumerRecord,
    error_reason: str,
    retry_count: int,
) -> None:
    dlq_topic = f"{msg.topic}.{settings.kafka_dlq_suffix}"
    dlq_payload = json.dumps({
        "original_message": msg.value.decode("utf-8", errors="replace"),
        "error_reason": error_reason,
        "retry_count": retry_count,
        "topic": msg.topic,
        "partition": msg.partition,
        "offset": msg.offset,
    })
    await producer.send(
        topic=dlq_topic,
        key=msg.key.decode("utf-8", errors="replace") if msg.key else "",
        value=dlq_payload,
    )
    logger.warning(
        "Message sent to DLQ %s from topic=%s offset=%s",
        dlq_topic,
        msg.topic,
        msg.offset,
    )
