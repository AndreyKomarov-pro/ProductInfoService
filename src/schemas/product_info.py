from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProductInfoBody(BaseModel):
    product_id: UUID
    rating: Decimal = Field(default=Decimal("0"), ge=0, le=5)
    reviews_count: int = Field(default=0, ge=0)
    warehouse_stock: int = Field(default=0, ge=0)


class ProductInfoCreate(BaseModel):
    body: ProductInfoBody


class ProductInfoUpdateBody(BaseModel):
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    reviews_count: int | None = Field(default=None, ge=0)
    warehouse_stock: int | None = Field(default=None, ge=0)


class ProductInfoUpdate(BaseModel):
    body: ProductInfoUpdateBody


class ProductInfoResponse(BaseModel):
    id: UUID
    product_id: UUID
    rating: Decimal
    reviews_count: int
    warehouse_stock: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "ProductInfoResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models) -> list["ProductInfoResponse"]:
        return [cls.model_validate(m) for m in models]
