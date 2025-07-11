"""Create Stock Price

Revision ID: cbd5fa9c8ea2
Revises:
Create Date: 2025-07-04 20:57:46.392426

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from collections.abc import Sequence
from typing import Union


# revision identifiers, used by Alembic.
revision: str = "cbd5fa9c8ea2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "stock_prices",
        sa.Column("ticker", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("open", sa.Float(), nullable=True),
        sa.Column("high", sa.Float(), nullable=True),
        sa.Column("low", sa.Float(), nullable=True),
        sa.Column("close", sa.Float(), nullable=True),
        sa.Column("volume", sa.Float(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.DateTime(), nullable=True),
        sa.Column("updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stock_prices_id"),
        "stock_prices",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stock_prices_ticker"),
        "stock_prices",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        op.f("ix_stock_prices_timestamp"),
        "stock_prices",
        ["timestamp"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_stock_prices_timestamp"), table_name="stock_prices")
    op.drop_index(op.f("ix_stock_prices_ticker"), table_name="stock_prices")
    op.drop_index(op.f("ix_stock_prices_id"), table_name="stock_prices")
    op.drop_table("stock_prices")
    # ### end Alembic commands ###
