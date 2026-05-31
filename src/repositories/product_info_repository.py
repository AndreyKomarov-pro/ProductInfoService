from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product_info import ProductInfoModel


class ProductInfoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_product_id(self, product_id: UUID) -> ProductInfoModel | None:
        result = await self.session.execute(
            select(ProductInfoModel)
            .where(
                ProductInfoModel.product_id == product_id,
                ProductInfoModel.is_deleted == False,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, obj: ProductInfoModel) -> ProductInfoModel:
        self.session.add(obj)
        await self.session.flush()
        return obj
