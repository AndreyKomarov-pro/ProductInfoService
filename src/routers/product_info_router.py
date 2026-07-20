from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from src.dependencies import get_product_info_service
from src.schemas.product_info import ProductInfoCreate, ProductInfoResponse
from src.services.product_info_service import ProductInfoService

router = APIRouter(tags=["ProductInfo"])


@router.get("/products/{product_id}/info", response_model=ProductInfoResponse)
async def get_product_info(
    product_id: UUID,
    service: ProductInfoService = Depends(get_product_info_service),
) -> ProductInfoResponse:
    return await service.get_by_product_id(product_id)


@router.post("/products/info", response_model=ProductInfoResponse, status_code=HTTPStatus.CREATED)
async def create_product_info(
    data: ProductInfoCreate,
    service: ProductInfoService = Depends(get_product_info_service),
) -> ProductInfoResponse:
    return await service.create(data)
