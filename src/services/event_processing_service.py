import logging
from uuid import UUID

from src.models.processed_event import ProcessedEventModel
from src.repositories.processed_event_repository import ProcessedEventRepository
from src.repositories.product_info_repository import ProductInfoRepository

logger = logging.getLogger(__name__)


class EventProcessingService:
    def __init__(
        self,
        processed_event_repo: ProcessedEventRepository,
        product_info_repo: ProductInfoRepository,
    ) -> None:
        self.processed_event_repo = processed_event_repo
        self.product_info_repo = product_info_repo

    async def process(
        self,
        event_id: UUID,
        topic: str,
        event_type: str,
        product_id: UUID,
    ) -> bool:
        is_new = await self.processed_event_repo.save_if_not_exists(
            ProcessedEventModel(
                event_id=event_id,
                topic=topic,
                event_type=event_type,
            )
        )
        if not is_new:
            return False

        created = await self.product_info_repo.create_if_not_exists(product_id)
        if created:
            logger.info("Created product info for product_id=%s", product_id)

        return True
