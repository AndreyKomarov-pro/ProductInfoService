from http import HTTPStatus

from fastapi import APIRouter, Depends, Query

from src.dependencies import get_product_info_service
from src.schemas.product_info import ProductInfoCreate, ProductInfoResponse
from src.schemas.pagination import PageResponse
from src.services.product_info_service import ProductInfoService

router = APIRouter(tags=["ProductInfo"])


@router.get("/products/info", response_model=PageResponse[ProductInfoResponse])
async def list_product_infos(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: ProductInfoService = Depends(get_product_info_service),
) -> PageResponse[ProductInfoResponse]:
    return await service.get_all(page, size)


@router.post("/products/info", response_model=ProductInfoResponse, status_code=HTTPStatus.CREATED)
async def create_product_info(
    data: ProductInfoCreate,
    service: ProductInfoService = Depends(get_product_info_service),
) -> ProductInfoResponse:
    return await service.create(data)
