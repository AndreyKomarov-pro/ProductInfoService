import logging
from uuid import UUID

from src.exceptions.not_found import NotFoundException
from src.models.processed_event import ProcessedEventModel
from src.models.product_info import ProductInfoModel
from src.repositories.processed_event_repository import ProcessedEventRepository
from src.repositories.product_info_repository import ProductInfoRepository
from src.schemas.product_info import ProductInfoCreate, ProductInfoResponse

logger = logging.getLogger(__name__)


class ProductInfoService:
    def __init__(
        self,
        repo: ProductInfoRepository,
        processed_event_repo: ProcessedEventRepository,
    ) -> None:
        self.repo = repo
        self.processed_event_repo = processed_event_repo

    async def _get_product_info_orm(self, product_id: UUID) -> ProductInfoModel:
        info = await self.repo.get_by_product_id(product_id)
        if info is None:
            logger.warning("ProductInfo not found for product_id=%s", product_id)
            raise NotFoundException("ProductInfo", product_id)
        return info

    async def get_by_product_id(self, product_id: UUID) -> ProductInfoResponse:
        logger.info("Fetching product info for product_id=%s", product_id)
        info = await self._get_product_info_orm(product_id)
        return ProductInfoResponse.from_model(info)

    async def create(self, data: ProductInfoCreate) -> ProductInfoResponse:
        logger.info("Creating product info for product_id=%s", data.product_id)
        obj = data.to_model()
        result = await self.repo.create(obj)
        return ProductInfoResponse.from_model(result)

    async def handle_event(
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

        info = await self.repo.get_by_product_id(product_id)
        if info is None:
            logger.info("Creating product info from event for product_id=%s", product_id)
            await self.repo.create(ProductInfoModel(product_id=product_id))

        return True
