from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.shared.enums import RecordStatus


class GrindingLedgerEntry(Base):
    __tablename__ = "grinding_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_jalali: Mapped[str] = mapped_column(String(10), nullable=False)
    date_gregorian: Mapped[date] = mapped_column(Date, nullable=False)
    facility: Mapped[str] = mapped_column(String(30), nullable=False)
    input_tonnage_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tonnage_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    waste_tonnage_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grinding_cost_rials: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    transport_cost_rials: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_cost_rials: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    receipt_number: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=RecordStatus.REGISTERED.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
