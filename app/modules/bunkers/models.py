from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.shared.enums import RecordStatus


class BunkerLoad(Base):
    __tablename__ = "bunker_loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_jalali: Mapped[str] = mapped_column(String(10), nullable=False)
    date_gregorian: Mapped[date] = mapped_column(Date, nullable=False)
    source_facility: Mapped[str] = mapped_column(String(30), nullable=False)
    receipt_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    tonnage_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    truck_plate_number: Mapped[str] = mapped_column(String(20), nullable=False)
    driver_name: Mapped[str] = mapped_column(String, nullable=False)
    cost_per_ton_rials: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    total_cost_rials: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
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
