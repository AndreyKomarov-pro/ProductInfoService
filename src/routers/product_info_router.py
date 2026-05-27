from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query

from src.dependencies import get_product_info_service
from src.schemas.product_info import (
    ProductInfoCreate,
    ProductInfoUpdate,
    ProductInfoResponse,
)
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


@router.put("/products/{product_id}/info", response_model=ProductInfoResponse)
async def update_product_info(
    product_id: UUID,
    data: ProductInfoUpdate,
    service: ProductInfoService = Depends(get_product_info_service),
) -> ProductInfoResponse:
    return await service.update(product_id, data)


@router.delete("/products/{product_id}/info", status_code=HTTPStatus.NO_CONTENT)
async def delete_product_info(
    product_id: UUID,
    service: ProductInfoService = Depends(get_product_info_service),
) -> None:
    await service.delete(product_id)
