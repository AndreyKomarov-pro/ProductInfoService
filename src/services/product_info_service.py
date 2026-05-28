import logging

from src.repositories.product_info_repository import ProductInfoRepository
from src.schemas.product_info import ProductInfoCreate, ProductInfoResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)


class ProductInfoService:
    def __init__(self, repo: ProductInfoRepository) -> None:
        self.repo = repo

    async def get_all(self, page: int, size: int) -> PageResponse[ProductInfoResponse]:
        logger.info("Fetching product infos page=%d size=%d", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse(
            items=ProductInfoResponse.from_list(items),
            page=page,
            size=size,
        )

    async def create(self, data: ProductInfoCreate) -> ProductInfoResponse:
        logger.info("Creating product info for product_id=%s", data.product_id)
        obj = data.to_model()
        result = await self.repo.create(obj)
        return ProductInfoResponse.from_model(result)
