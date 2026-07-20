from typing import Self
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.exceptions.validation import ValidationException
from src.models.product_info import ProductInfoModel


class ProductInfoCreate(BaseModel):
    product_id: UUID
    rating: Decimal = Field(default=Decimal("0"))
    reviews_count: int = Field(default=0)
    warehouse_stock: int = Field(default=0)

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, value: Decimal) -> Decimal:
        if value < 0 or value > 5:
            raise ValidationException("rating", "Rating must be between 0 and 5")
        return value

    @field_validator("reviews_count")
    @classmethod
    def validate_reviews_count(cls, value: int) -> int:
        if value < 0:
            raise ValidationException("reviews_count", "Reviews count must be non-negative")
        return value

    @field_validator("warehouse_stock")
    @classmethod
    def validate_warehouse_stock(cls, value: int) -> int:
        if value < 0:
            raise ValidationException("warehouse_stock", "Warehouse stock must be non-negative")
        return value

    def to_model(self) -> ProductInfoModel:
        return ProductInfoModel(**self.model_dump())


class ProductInfoResponse(BaseModel):
    id: UUID
    product_id: UUID
    rating: Decimal
    reviews_count: int
    warehouse_stock: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: ProductInfoModel) -> Self:
        return cls.model_validate(model)
