"""initial

Revision ID: 001
Revises:
Create Date: 2026-05-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('product_infos',
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=False),
    sa.Column('reviews_count', sa.Integer(), nullable=False),
    sa.Column('warehouse_stock', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id'),
    )


def downgrade() -> None:
    op.drop_table('product_infos')
