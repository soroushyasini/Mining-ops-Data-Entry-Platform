"""
Seed script to insert sample records for testing.
Run with: docker compose exec api python scripts/seed_data.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.modules.drivers.models import Driver
from app.modules.cars.models import Car
from app.modules.trucks.models import TruckLoad
from app.shared.jalali import jalali_to_gregorian
from app.shared.enums import RecordStatus

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

DRIVERS = [
    {"full_name": "حسین طاووسی باغسیاه", "iban": "IR290190000000102529858002", "phone": "9155188319"},
    {"full_name": "حمید دائمی ابراهیم زاده", "iban": "IR790190000000101103999006", "phone": "9109825710"},
    {"full_name": "محمد احمد آبادی", "iban": None, "phone": None},
    {"full_name": "حبیب احمدآبادی", "iban": None, "phone": None},
    {"full_name": "هادی احمدآبادی", "iban": None, "phone": None},
    {"full_name": "محمدرضا احمدآبادی", "iban": None, "phone": None},
    {"full_name": "احمد عرفانیان", "iban": "IR070120000000009101189676", "phone": "9151810135"},
    {"full_name": "حسن رضوی", "iban": "IR350130100000000053900080", "phone": "9153070667"},
    {"full_name": "مهدی نصرابادی", "iban": "IR070120000000009101189676", "phone": "9151183744"},
    {"full_name": "مصطفی صاحبی", "iban": "IR910750022110967000055116", "phone": "9157089310"},
]

CARS = [
    {"plate_number": "14978"},
    {"plate_number": "81375"},
    {"plate_number": "23911"},
    {"plate_number": "97966"},
    {"plate_number": "48297"},
    {"plate_number": "74281"},
    {"plate_number": "14434"},
    {"plate_number": "98176"},
    {"plate_number": "63643"},
    {"plate_number": "65495"},
]

TRUCK_LOADS = [
    {"date_jalali": "1404/11/12", "truck_plate_number": "14978", "receipt_number": 2823, "tonnage_kg": 27170, "destination": "robat_sefid", "cost_per_ton_rials": 8700000, "driver_name": "محمد احمد آبادی", "status": "registered"},
    {"date_jalali": "1404/11/12", "truck_plate_number": "81375", "receipt_number": 2824, "tonnage_kg": 10310, "destination": "robat_sefid", "cost_per_ton_rials": 8700000, "driver_name": "حبیب احمدآبادی", "status": "registered"},
    {"date_jalali": "1404/11/13", "truck_plate_number": "23911", "receipt_number": 2835, "tonnage_kg": 26090, "destination": "robat_sefid", "cost_per_ton_rials": 8700000, "driver_name": "هادی احمدآبادی", "status": "registered"},
    {"date_jalali": "1404/11/13", "truck_plate_number": "97966", "receipt_number": 2836, "tonnage_kg": 24870, "destination": "robat_sefid", "cost_per_ton_rials": 8700000, "driver_name": "محمدرضا احمدآبادی", "status": "registered"},
    {"date_jalali": "1404/11/14", "truck_plate_number": "14978", "receipt_number": 2849, "tonnage_kg": 26150, "destination": "robat_sefid", "cost_per_ton_rials": 8700000, "driver_name": "محمد احمد آبادی", "status": "registered"},
]


async def seed():
    async with AsyncSessionLocal() as session:
        # Seed Drivers
        drivers_created = 0
        driver_map = {}
        for d in DRIVERS:
            existing = await session.execute(
                select(Driver).where(Driver.full_name == d["full_name"])
            )
            existing_driver = existing.scalar_one_or_none()
            if existing_driver:
                driver_map[d["full_name"]] = existing_driver
                continue
            driver = Driver(**d)
            session.add(driver)
            await session.flush()
            driver_map[d["full_name"]] = driver
            drivers_created += 1
        await session.commit()
        print(f"Drivers created: {drivers_created}")

        # Seed Cars (with driver links based on known data)
        car_driver_links = {
            "14978": "محمد احمد آبادی",
            "81375": "حبیب احمدآبادی",
            "23911": "هادی احمدآبادی",
            "97966": "محمدرضا احمدآبادی",
        }
        cars_created = 0
        for c in CARS:
            existing = await session.execute(
                select(Car).where(Car.plate_number == c["plate_number"])
            )
            if existing.scalar_one_or_none():
                continue
            driver_name = car_driver_links.get(c["plate_number"])
            driver_id = driver_map[driver_name].id if driver_name and driver_name in driver_map else None
            car = Car(plate_number=c["plate_number"], current_driver_id=driver_id)
            session.add(car)
            cars_created += 1
        await session.commit()
        print(f"Cars created: {cars_created}")

        # Seed Truck Loads
        trucks_created = 0
        for t in TRUCK_LOADS:
            existing = await session.execute(
                select(TruckLoad).where(TruckLoad.receipt_number == t["receipt_number"])
            )
            if existing.scalar_one_or_none():
                continue
            greg_date = jalali_to_gregorian(t["date_jalali"])
            truck = TruckLoad(
                date_jalali=t["date_jalali"],
                date_gregorian=greg_date,
                truck_plate_number=t["truck_plate_number"],
                receipt_number=t["receipt_number"],
                tonnage_kg=t["tonnage_kg"],
                destination=t["destination"],
                cost_per_ton_rials=t.get("cost_per_ton_rials"),
                total_cost_rials=t.get("total_cost_rials"),
                driver_name=t["driver_name"],
                notes=t.get("notes"),
                status=t.get("status", RecordStatus.REGISTERED.value),
            )
            session.add(truck)
            trucks_created += 1
        await session.commit()
        print(f"Truck loads created: {trucks_created}")
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
