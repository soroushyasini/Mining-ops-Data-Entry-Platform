from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PaymentGroup(Base):
    __tablename__ = "payment_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_date_jalali: Mapped[str] = mapped_column(String(10), nullable=False)
    payment_date_gregorian: Mapped[date] = mapped_column(Date, nullable=False)
    payment_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    payer_name: Mapped[str] = mapped_column(String, nullable=False)
    bank_name: Mapped[str] = mapped_column(String, nullable=False)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_amount_rials: Mapped[int] = mapped_column(BigInteger, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("payment_groups.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_rials: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
