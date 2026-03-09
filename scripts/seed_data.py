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
from app.modules.bunkers.models import BunkerLoad
from app.modules.lab.models import LabIssueBatch, LabResult
from app.modules.grinding.models import GrindingLedgerEntry
from app.modules.payments.models import PaymentGroup, Payment
from app.shared.jalali import jalali_to_gregorian
from app.shared.enums import RecordStatus
from app.shared.sample_parser import parse_sample_code

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

BUNKER_LOADS = [
    {"date_jalali": "1404/11/04", "source_facility": "robat_sefid", "receipt_number": 2271, "tonnage_kg": 23560, "truck_plate_number": "14978", "driver_name": "محمد احمد آبادی"},
    {"date_jalali": "1404/11/08", "source_facility": "robat_sefid", "receipt_number": 2280, "tonnage_kg": 24810, "truck_plate_number": "81375", "driver_name": "حبیب احمدآبادی"},
    {"date_jalali": "1404/11/09", "source_facility": "shen_beton", "receipt_number": 2283, "tonnage_kg": 18760, "truck_plate_number": "23911", "driver_name": "هادی احمدآبادی"},
    {"date_jalali": "1404/11/09", "source_facility": "robat_sefid", "receipt_number": 2281, "tonnage_kg": 25900, "truck_plate_number": "97966", "driver_name": "محمدرضا احمدآبادی"},
    {"date_jalali": "1404/11/09", "source_facility": "robat_sefid", "receipt_number": 2279, "tonnage_kg": 22580, "truck_plate_number": "48297", "driver_name": "احمد عرفانیان"},
]

LAB_BATCHES = [
    {"issue_date_jalali": "1404/11/08"},
    {"issue_date_jalali": "1404/11/10"},
]

LAB_RESULTS_BATCH_1 = [
    {"sample_code": "A-1404/11/08-K-1", "gold_ppm": 1.45},
    {"sample_code": "A-1404/11/08-K-2", "gold_ppm": 1.62},
    {"sample_code": "A-1404/11/08-L-1", "gold_ppm": 0.28},
    {"sample_code": "A-1404/11/08-CR-1", "gold_ppm": 485.0},
    {"sample_code": "A-1404/11/08-T-1", "gold_ppm": 0.09},
]

LAB_RESULTS_BATCH_2 = [
    {"sample_code": "B-1404/11/10-K-1", "gold_ppm": 1.38},
    {"sample_code": "B-1404/11/10-L-1", "gold_ppm": 0.31},
    {"sample_code": "B-1404/11/10-CR-1", "gold_ppm": 472.0},
    {"sample_code": "RC-1404/11/10-1", "gold_ppm": 0.02},
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

        # Seed Bunker Loads
        bunkers_created = 0
        for b in BUNKER_LOADS:
            existing = await session.execute(
                select(BunkerLoad).where(BunkerLoad.receipt_number == b["receipt_number"])
            )
            if existing.scalar_one_or_none():
                continue
            greg_date = jalali_to_gregorian(b["date_jalali"])
            bunker = BunkerLoad(
                date_jalali=b["date_jalali"],
                date_gregorian=greg_date,
                source_facility=b["source_facility"],
                receipt_number=b["receipt_number"],
                tonnage_kg=b["tonnage_kg"],
                truck_plate_number=b["truck_plate_number"],
                driver_name=b["driver_name"],
                status=RecordStatus.REGISTERED.value,
            )
            session.add(bunker)
            bunkers_created += 1
        await session.commit()
        print(f"Bunker loads created: {bunkers_created}")

        # Seed Lab Batches and Results
        batches_created = 0
        batch_map = {}
        for lb in LAB_BATCHES:
            existing = await session.execute(
                select(LabIssueBatch).where(LabIssueBatch.issue_date_jalali == lb["issue_date_jalali"])
            )
            existing_batch = existing.scalar_one_or_none()
            if existing_batch:
                batch_map[lb["issue_date_jalali"]] = existing_batch
                continue
            greg_date = jalali_to_gregorian(lb["issue_date_jalali"])
            batch = LabIssueBatch(
                issue_date_jalali=lb["issue_date_jalali"],
                issue_date_gregorian=greg_date,
                status=RecordStatus.REGISTERED.value,
            )
            session.add(batch)
            await session.flush()
            batch_map[lb["issue_date_jalali"]] = batch
            batches_created += 1
        await session.commit()
        print(f"Lab batches created: {batches_created}")

        results_created = 0
        batch_1 = batch_map.get("1404/11/08")
        batch_2 = batch_map.get("1404/11/10")

        for results_list, batch in [
            (LAB_RESULTS_BATCH_1, batch_1),
            (LAB_RESULTS_BATCH_2, batch_2),
        ]:
            if not batch:
                continue
            for r in results_list:
                existing = await session.execute(
                    select(LabResult).where(LabResult.sample_code == r["sample_code"])
                )
                if existing.scalar_one_or_none():
                    continue
                parsed = parse_sample_code(r["sample_code"])
                sample_date_gregorian = None
                if parsed.get("sample_date_jalali"):
                    try:
                        sample_date_gregorian = jalali_to_gregorian(parsed["sample_date_jalali"])
                    except ValueError:
                        pass
                lab_result = LabResult(
                    batch_id=batch.id,
                    sample_code=r["sample_code"],
                    gold_ppm=r["gold_ppm"],
                    source_facility=parsed.get("source_facility"),
                    sample_date_jalali=parsed.get("sample_date_jalali"),
                    sample_date_gregorian=sample_date_gregorian,
                    sample_type=parsed.get("sample_type"),
                    sequence_number=parsed.get("sequence_number"),
                )
                session.add(lab_result)
                results_created += 1
        await session.commit()
        print(f"Lab results created: {results_created}")

        # Seed Grinding Ledger Entries
        GRINDING_ENTRIES = [
            {"date_jalali": "1404/11/04", "facility": "robat_sefid", "input_tonnage_kg": 23560, "output_tonnage_kg": 22800, "grinding_cost_rials": 45000000, "total_cost_rials": 45000000},
            {"date_jalali": "1404/11/05", "facility": "robat_sefid", "input_tonnage_kg": 25100, "output_tonnage_kg": 24300, "grinding_cost_rials": 47000000, "total_cost_rials": 47000000},
            {"date_jalali": "1404/11/06", "facility": "shen_beton", "input_tonnage_kg": 18900, "output_tonnage_kg": 18200, "grinding_cost_rials": 38000000, "total_cost_rials": 38000000},
            {"date_jalali": "1404/11/08", "facility": "robat_sefid", "input_tonnage_kg": 24810, "notes": "Pending cost from bureau"},
            {"date_jalali": "1404/11/09", "facility": "shen_beton", "input_tonnage_kg": 18760, "notes": "Pending cost from bureau"},
        ]
        grinding_created = 0
        grinding_map = {}
        for g in GRINDING_ENTRIES:
            existing = await session.execute(
                select(GrindingLedgerEntry).where(
                    GrindingLedgerEntry.date_jalali == g["date_jalali"],
                    GrindingLedgerEntry.facility == g["facility"],
                )
            )
            existing_entry = existing.scalar_one_or_none()
            if existing_entry:
                key = (g["date_jalali"], g["facility"])
                grinding_map[key] = existing_entry
                continue
            greg_date = jalali_to_gregorian(g["date_jalali"])
            # Entries with cost fields start as "costed", others as "registered"
            has_cost = g.get("grinding_cost_rials") is not None or g.get("total_cost_rials") is not None
            entry_status = RecordStatus.COSTED.value if has_cost else RecordStatus.REGISTERED.value
            entry = GrindingLedgerEntry(
                date_jalali=g["date_jalali"],
                date_gregorian=greg_date,
                facility=g["facility"],
                input_tonnage_kg=g["input_tonnage_kg"],
                output_tonnage_kg=g.get("output_tonnage_kg"),
                grinding_cost_rials=g.get("grinding_cost_rials"),
                total_cost_rials=g.get("total_cost_rials"),
                notes=g.get("notes"),
                status=entry_status,
            )
            session.add(entry)
            await session.flush()
            key = (g["date_jalali"], g["facility"])
            grinding_map[key] = entry
            grinding_created += 1
        await session.commit()
        print(f"Grinding ledger entries created: {grinding_created}")

        # Seed Payment Groups — link first two costed grinding entries
        g1 = grinding_map.get(("1404/11/04", "robat_sefid"))
        g2 = grinding_map.get(("1404/11/05", "robat_sefid"))
        payment_groups_created = 0
        if g1 and g2 and g1.status == RecordStatus.COSTED.value and g2.status == RecordStatus.COSTED.value:
            existing_pg = await session.execute(
                select(PaymentGroup).where(PaymentGroup.payment_date_jalali == "1404/11/15")
            )
            if not existing_pg.scalar_one_or_none():
                pg = PaymentGroup(
                    payment_date_jalali="1404/11/15",
                    payment_date_gregorian=jalali_to_gregorian("1404/11/15"),
                    payer_name="شرکت معدن طلا",
                    bank_name="بانک ملی",
                    total_amount_rials=92000000,
                )
                session.add(pg)
                await session.flush()
                session.add(Payment(group_id=pg.id, entity_type="grinding", entity_id=g1.id, amount_rials=45000000))
                session.add(Payment(group_id=pg.id, entity_type="grinding", entity_id=g2.id, amount_rials=47000000))
                g1.status = RecordStatus.PAID.value
                g2.status = RecordStatus.PAID.value
                await session.commit()
                payment_groups_created += 1
        print(f"Payment groups created: {payment_groups_created}")
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
