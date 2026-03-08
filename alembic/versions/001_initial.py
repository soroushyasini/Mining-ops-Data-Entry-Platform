"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("iban", sa.String(length=34), nullable=True),
        sa.Column("phone", sa.String(length=15), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plate_number", sa.String(length=20), nullable=False),
        sa.Column("current_driver_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["current_driver_id"], ["drivers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plate_number"),
    )

    op.create_table(
        "truck_loads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date_jalali", sa.String(length=10), nullable=False),
        sa.Column("date_gregorian", sa.Date(), nullable=False),
        sa.Column("truck_plate_number", sa.String(length=20), nullable=False),
        sa.Column("receipt_number", sa.Integer(), nullable=False),
        sa.Column("tonnage_kg", sa.Integer(), nullable=False),
        sa.Column("destination", sa.String(length=30), nullable=False),
        sa.Column("cost_per_ton_rials", sa.BigInteger(), nullable=True),
        sa.Column("total_cost_rials", sa.BigInteger(), nullable=True),
        sa.Column("driver_name", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="registered"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("receipt_number"),
    )

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("file_type", sa.String(length=10), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payment_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_date_jalali", sa.String(length=10), nullable=False),
        sa.Column("payment_date_gregorian", sa.Date(), nullable=False),
        sa.Column("payment_time", sa.Time(), nullable=True),
        sa.Column("payer_name", sa.String(), nullable=False),
        sa.Column("bank_name", sa.String(), nullable=False),
        sa.Column("bank_account_number", sa.String(), nullable=True),
        sa.Column("total_amount_rials", sa.BigInteger(), nullable=False),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("amount_rials", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["payment_groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("payment_groups")
    op.drop_table("attachments")
    op.drop_table("truck_loads")
    op.drop_table("cars")
    op.drop_table("drivers")
