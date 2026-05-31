import logging
from uuid import UUID

from src.exceptions.not_found import NotFoundException
from src.models.product_info import ProductInfoModel
from src.repositories.product_info_repository import ProductInfoRepository
from src.schemas.product_info import ProductInfoCreate, ProductInfoResponse

logger = logging.getLogger(__name__)


class ProductInfoService:
    def __init__(self, repo: ProductInfoRepository) -> None:
        self.repo = repo

    async def _get_product_info_orm(self, product_id: UUID) -> ProductInfoModel:
        info = await self.repo.get_by_product_id(product_id)
        if not info:
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
