import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from aiokafka.structs import ConsumerRecord

from src.clients.kafka_producer import KafkaProducer
from src.config import settings
from src.db import SessionFactory
from src.models.processed_event import ProcessedEventModel
from src.repositories.processed_event_repository import ProcessedEventRepository

logger = logging.getLogger(__name__)


async def consume_events(producer: KafkaProducer) -> None:
    consumer = AIOKafkaConsumer(
        *settings.kafka_topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: v.decode("utf-8"),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
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
        envelope = json.loads(msg.value)
        event_id = UUID(envelope["event_id"])
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("Non-retryable parse error: %s", exc)
        await _send_to_dlq(producer, msg, str(exc), 0)
        await consumer.commit()
        return

    for attempt in range(1, settings.kafka_consumer_max_retries + 1):
        try:
            async with SessionFactory() as session:
                repo = ProcessedEventRepository(session)
                saved = await repo.save_if_not_exists(
                    ProcessedEventModel(
                        event_id=event_id,
                        topic=msg.topic,
                        event_type=envelope["event_type"],
                    )
                )
                if not saved:
                    logger.debug("Duplicate event %s, skipping", event_id)
                    break
                await session.commit()
            logger.info(
                "Processed event %s type=%s from %s",
                event_id,
                envelope["event_type"],
                msg.topic,
            )
            break
        except Exception as exc:
            logger.warning(
                "Attempt %d/%d failed for event %s: %s",
                attempt,
                settings.kafka_consumer_max_retries,
                event_id,
                exc,
            )
            if attempt == settings.kafka_consumer_max_retries:
                await _send_to_dlq(producer, msg, str(exc), attempt)
            else:
                await asyncio.sleep(settings.kafka_consumer_retry_delay)

    await consumer.commit()


async def _send_to_dlq(
    producer: KafkaProducer,
    msg: ConsumerRecord,
    error_reason: str,
    retry_count: int,
) -> None:
    dlq_topic = f"{msg.topic}.{settings.kafka_dlq_suffix}"
    dlq_payload = json.dumps({
        "original_message": msg.value if isinstance(msg.value, str) else msg.value.decode("utf-8"),
        "error_reason": error_reason,
        "retry_count": retry_count,
        "topic": msg.topic,
        "partition": msg.partition,
        "offset": msg.offset,
    })
    await producer.send(
        topic=dlq_topic,
        key=msg.key or "",
        value=dlq_payload,
    )
    logger.warning(
        "Message sent to DLQ %s from topic=%s offset=%s",
        dlq_topic,
        msg.topic,
        msg.offset,
    )
