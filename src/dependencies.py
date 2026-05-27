from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.product_info_repository import ProductInfoRepository
from src.services.product_info_service import ProductInfoService


def get_product_info_service(
    session: AsyncSession = Depends(get_db),
) -> ProductInfoService:
    return ProductInfoService(ProductInfoRepository(session))
