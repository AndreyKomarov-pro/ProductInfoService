"""add processed events

Revision ID: 002
Revises: 001
Create Date: 2026-08-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('processed_events',
    sa.Column('event_id', sa.Uuid(), nullable=False),
    sa.Column('topic', sa.String(length=100), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('event_id'),
    )


def downgrade() -> None:
    op.drop_table('processed_events')
