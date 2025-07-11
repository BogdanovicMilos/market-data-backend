"""Add unique

Revision ID: 4a63d4911a67
Revises: 2b9470abc496
Create Date: 2025-07-05 19:55:10.384323

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from collections.abc import Sequence
from typing import Union


# revision identifiers, used by Alembic.
revision: str = "4a63d4911a67"
down_revision: str | None = "2b9470abc496"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        "uq_ticker_timestamp",
        "stock_prices",
        ["ticker", "timestamp"],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("uq_ticker_timestamp", "stock_prices", type_="unique")
    # ### end Alembic commands ###
