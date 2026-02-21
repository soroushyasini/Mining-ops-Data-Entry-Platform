import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime,
    ForeignKey, UniqueConstraint, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class FacilityCode(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class DriverStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class TruckStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class PaymentType(str, enum.Enum):
    owed = "owed"
    paid = "paid"


class AlertLevel(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(SAEnum(FacilityCode), unique=True, nullable=False)
    name_fa = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    bunker_sheet_name = Column(String(100), nullable=True)
    truck_destination = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    shipments = relationship("Shipment", back_populates="facility")
    bunker_loads = relationship("BunkerLoad", back_populates="facility")
    lab_samples = relationship("LabSample", back_populates="facility")
    transport_costs = relationship("TransportCost", back_populates="facility")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(200), nullable=False, unique=True)
    aliases = Column(JSON, default=list)
    status = Column(SAEnum(DriverStatus), default=DriverStatus.active)
    bank_account = Column(String(30), nullable=True)
    phone = Column(String(15), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    shipments = relationship("Shipment", back_populates="driver")
    bunker_loads = relationship("BunkerLoad", back_populates="driver")
    payments = relationship("Payment", back_populates="driver")


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), nullable=False, unique=True)
    status = Column(SAEnum(TruckStatus), default=TruckStatus.active)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    shipments = relationship("Shipment", back_populates="truck")


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False)  # Jalali YYYY/MM/DD
    receipt_number = Column(String(50), nullable=True)
    tonnage_kg = Column(Float, nullable=False)
    destination = Column(String(200), nullable=True)
    cost_per_ton_rial = Column(Float, nullable=True)
    total_cost_rial = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    facility = relationship("Facility", back_populates="shipments")
    driver = relationship("Driver", back_populates="shipments")
    truck = relationship("Truck", back_populates="shipments")


class BunkerLoad(Base):
    __tablename__ = "bunker_loads"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False)          # Jalali YYYY/MM/DD — تاریخ
    time = Column(String(5), nullable=True)             # HH:MM — ساعت
    truck_number_raw = Column(String(20), nullable=True) # شماره ماشین (raw, for reference)
    receipt_number = Column(String(50), nullable=True)  # شماره قبض
    tonnage_kg = Column(Float, nullable=False)          # تناژ
    origin = Column(String(200), nullable=True)         # مبدا
    cost_per_ton_rial = Column(Float, nullable=True)    # هزینه حمل هر تن
    total_cost_rial = Column(Float, nullable=True)      # مبلغ (ریال) = tonnage × cost_per_ton
    notes = Column(Text, nullable=True)                 # توضیحات
    # Legacy fields kept for backward compat
    cumulative_tonnage_kg = Column(Float, nullable=True)
    sheet_name = Column(String(100), nullable=True)
    # Foreign keys
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    facility = relationship("Facility", back_populates="bunker_loads")
    driver = relationship("Driver", back_populates="bunker_loads")


class LabSample(Base):
    __tablename__ = "lab_samples"

    id = Column(Integer, primary_key=True, index=True)
    sample_code = Column(String(100), nullable=False)
    sheet_name = Column(String(100), nullable=False)
    au_ppm = Column(Float, nullable=True)
    au_detected = Column(Boolean, default=True)
    below_detection_limit = Column(Boolean, default=False)
    sample_type = Column(String(50), nullable=True)
    date = Column(String(10), nullable=True)  # Jalali YYYY/MM/DD
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)
    day = Column(Integer, nullable=True)
    sample_number = Column(Integer, nullable=True)
    is_special = Column(Boolean, default=False)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    facility = relationship("Facility", back_populates="lab_samples")

    __table_args__ = (
        UniqueConstraint("sample_code", "sheet_name", name="uq_lab_sample_code_sheet"),
    )


class TransportCost(Base):
    __tablename__ = "transport_costs"

    id = Column(Integer, primary_key=True, index=True)
    route = Column(String(200), nullable=False)
    cost_per_ton_rial = Column(Float, nullable=False)
    valid_from = Column(String(10), nullable=True)  # Jalali YYYY/MM/DD
    valid_to = Column(String(10), nullable=True)    # Jalali YYYY/MM/DD
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    facility = relationship("Facility", back_populates="transport_costs")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False)  # Jalali YYYY/MM/DD
    amount_rial = Column(Float, nullable=False)
    payment_type = Column(SAEnum(PaymentType), nullable=False)
    notes = Column(Text, nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    driver = relationship("Driver", back_populates="payments")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(SAEnum(AlertLevel), nullable=False, default=AlertLevel.info)
    rule = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
