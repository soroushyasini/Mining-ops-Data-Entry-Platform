from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.shared.enums import RecordStatus


class LabIssueBatch(Base):
    __tablename__ = "lab_issue_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issue_date_jalali: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    issue_date_gregorian: Mapped[date] = mapped_column(Date, nullable=False)
    analysis_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_cost_rials: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=RecordStatus.REGISTERED.value
    )
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    results: Mapped[list["LabResult"]] = relationship(
        "LabResult", back_populates="batch", cascade="all, delete-orphan"
    )


class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lab_issue_batches.id", ondelete="CASCADE"), nullable=False
    )
    sample_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    source_facility: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    sample_date_jalali: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    sample_date_gregorian: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sample_type: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    sequence_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gold_ppm: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    batch: Mapped["LabIssueBatch"] = relationship("LabIssueBatch", back_populates="results")
