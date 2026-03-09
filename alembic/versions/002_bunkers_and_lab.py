"""bunkers and lab tables

Revision ID: 002_bunkers_and_lab
Revises: 001_initial
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_bunkers_and_lab"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bunker_loads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date_jalali", sa.String(length=10), nullable=False),
        sa.Column("date_gregorian", sa.Date(), nullable=False),
        sa.Column("source_facility", sa.String(length=30), nullable=False),
        sa.Column("receipt_number", sa.Integer(), nullable=False),
        sa.Column("tonnage_kg", sa.Integer(), nullable=False),
        sa.Column("truck_plate_number", sa.String(length=20), nullable=False),
        sa.Column("driver_name", sa.String(), nullable=False),
        sa.Column("cost_per_ton_rials", sa.BigInteger(), nullable=True),
        sa.Column("total_cost_rials", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="registered"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("receipt_number"),
    )

    op.create_table(
        "lab_issue_batches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("issue_date_jalali", sa.String(length=10), nullable=False),
        sa.Column("issue_date_gregorian", sa.Date(), nullable=False),
        sa.Column("analysis_count", sa.Integer(), nullable=True),
        sa.Column("total_cost_rials", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="registered"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("issue_date_jalali"),
    )

    op.create_table(
        "lab_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("sample_code", sa.String(), nullable=False),
        sa.Column("source_facility", sa.String(length=30), nullable=True),
        sa.Column("sample_date_jalali", sa.String(length=10), nullable=True),
        sa.Column("sample_date_gregorian", sa.Date(), nullable=True),
        sa.Column("sample_type", sa.String(length=10), nullable=True),
        sa.Column("sequence_number", sa.Integer(), nullable=True),
        sa.Column("gold_ppm", sa.Numeric(10, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["lab_issue_batches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sample_code"),
    )


def downgrade() -> None:
    op.drop_table("lab_results")
    op.drop_table("lab_issue_batches")
    op.drop_table("bunker_loads")
