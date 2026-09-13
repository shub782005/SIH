"""Add updated_at to drivers

Revision ID: 706c9e4a8123
Revises: 705b8c9d1234
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "706c9e4a8123"
down_revision: Union[str, Sequence[str], None] = "705b8c9d1234"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "drivers",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE drivers SET updated_at = created_at WHERE updated_at IS NULL"
    )

    op.alter_column(
        "drivers",
        "updated_at",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("drivers", "updated_at")