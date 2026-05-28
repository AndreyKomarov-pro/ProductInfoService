from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.repositories.product_info_repository import ProductInfoRepository
from src.services.product_info_service import ProductInfoService


def get_product_info_service(
    session: AsyncSession = Depends(get_session),
) -> ProductInfoService:
    return ProductInfoService(ProductInfoRepository(session))
