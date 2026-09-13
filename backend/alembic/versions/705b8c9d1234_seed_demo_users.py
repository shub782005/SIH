"""Seed demo users

Revision ID: 705b8c9d1234
Revises: 704a77c49f7c
Create Date: 2026-09-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from app.core.security import get_password_hash


# revision identifiers, used by Alembic.
revision: str = "705b8c9d1234"
down_revision: Union[str, Sequence[str], None] = "704a77c49f7c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    demo_users = [
        {
            "name": "EcoRoute Admin",
            "email": "admin@ecoroute.org",
            "password": "Password123!",
            "role": "ADMIN",
        },
        {
            "name": "EcoRoute Manager",
            "email": "manager@ecoroute.org",
            "password": "Password123!",
            "role": "MANAGER",
        },
        {
            "name": "Rahul Driver",
            "email": "rahul@ecoroute.org",
            "password": "Password123!",
            "role": "DRIVER",
        },
    ]

    for user in demo_users:
        existing = connection.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": user["email"]},
        ).first()

        if not existing:
            connection.execute(
                text(
                    """
                    INSERT INTO users
                        (name, email, password_hash, role, created_at, updated_at)
                    VALUES
                        (:name, :email, :password_hash, :role, NOW(), NOW())
                    """
                ),
                {
                    "name": user["name"],
                    "email": user["email"],
                    "password_hash": get_password_hash(user["password"]),
                    "role": user["role"],
                },
            )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        text(
            """
            DELETE FROM users
            WHERE email IN (
                'admin@ecoroute.org',
                'manager@ecoroute.org',
                'rahul@ecoroute.org'
            )
            """
        )
    )