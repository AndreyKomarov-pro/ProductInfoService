from decimal import Decimal
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class ProductInfoModel(Base):
    __tablename__ = "product_infos"

    product_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False, unique=True)
    rating: Mapped[Decimal] = mapped_column(sa.Numeric(3, 2), default=Decimal("0"))
    reviews_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    warehouse_stock: Mapped[int] = mapped_column(sa.Integer, default=0)
