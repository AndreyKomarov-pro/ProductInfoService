import logging
from uuid import UUID

from src.exceptions import NotFoundException
from src.models.product_info import ProductInfoModel
from src.repositories.product_info_repository import ProductInfoRepository
from src.schemas.product_info import (
    ProductInfoCreate,
    ProductInfoUpdate,
    ProductInfoUpdateBody,
    ProductInfoResponse,
)
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)


class ProductInfoService:
    def __init__(self, repo: ProductInfoRepository) -> None:
        self.repo = repo

    async def _get_product_info_orm(self, product_id: UUID) -> ProductInfoModel:
        info = await self.repo.get_by_product_id(product_id)
        if not info:
            raise NotFoundException("ProductInfo", product_id)
        return info

    async def get_all(self, page: int, size: int) -> PageResponse[ProductInfoResponse]:
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse(
            items=ProductInfoResponse.from_list(items),
            page=page,
            size=size,
        )

    async def get_by_product_id(self, product_id: UUID) -> ProductInfoResponse:
        info = await self._get_product_info_orm(product_id)
        return ProductInfoResponse.from_model(info)

    async def create(self, data: ProductInfoCreate) -> ProductInfoResponse:
        logger.info("Creating product info for product_id=%s", data.body.product_id)
        obj = ProductInfoModel(
            product_id=data.body.product_id,
            rating=data.body.rating,
            reviews_count=data.body.reviews_count,
            warehouse_stock=data.body.warehouse_stock,
        )
        result = await self.repo.create(obj)
        return ProductInfoResponse.from_model(result)

    async def update(self, product_id: UUID, data: ProductInfoUpdate) -> ProductInfoResponse:
        logger.info("Updating product info for product_id=%s", product_id)
        info = await self._get_product_info_orm(product_id)
        self._update_fields(info, data.body)
        result = await self.repo.update(info)
        return ProductInfoResponse.from_model(result)

    async def delete(self, product_id: UUID) -> None:
        logger.info("Deleting product info for product_id=%s", product_id)
        info = await self._get_product_info_orm(product_id)
        await self.repo.delete(info)

    @staticmethod
    def _update_fields(obj: ProductInfoModel, fields: ProductInfoUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
