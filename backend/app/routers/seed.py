import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Driver, Truck, Facility

router = APIRouter(prefix="/seed", tags=["seed"])

DRIVERS = [
    {"canonical_name": "حسین طاووسی باغسیاه", "bank_account": "IR290190000000102529858002", "phone": "9155188319", "aliases": []},
    {"canonical_name": "حمید دائمی ابراهیم زاده", "bank_account": "IR790190000000101103999006", "phone": "9109825710", "aliases": ["حمید دائمی"]},
    {"canonical_name": "علی رضا طاووسی باغسیاه", "bank_account": "IR270190000000101447685007", "phone": "9153006809", "aliases": []},
    {"canonical_name": "محمد استیری", "bank_account": "IR560190000000100386782002", "phone": "9155085950", "aliases": []},
    {"canonical_name": "مهدی نصرابادی", "bank_account": "IR070120000000009101189676", "phone": "9151183744", "aliases": []},
    {"canonical_name": "حسن اکبری", "bank_account": "IR6701200100000007551857037", "phone": "9151183745", "aliases": []},
    {"canonical_name": "احمد عرفانیان", "bank_account": "IR070120000000009101189676", "phone": "9151810135", "aliases": []},
    {"canonical_name": "غلام حسین جوادی", "bank_account": "IR460170000000368784874005", "phone": "9153070667", "aliases": []},
    {"canonical_name": "حسن رضوی", "bank_account": "IR350130100000000053900080", "phone": "9153070667", "aliases": []},
    {"canonical_name": "مصطفی صاحبی", "bank_account": "IR910750022110967000055116", "phone": "9157089310", "aliases": []},
]

TRUCKS = [
    {"number": "14434", "status": "active"},
    {"number": "48297", "status": "active"},
    {"number": "63643", "status": "active"},
    {"number": "65495", "status": "active"},
    {"number": "74281", "status": "active"},
]

FACILITIES = [
    {"code": "A", "name_fa": "حجازیان", "name_en": "Hejazian", "bunker_sheet_name": "بونکر A", "truck_destination": "رباط سفید"},
    {"code": "B", "name_fa": "تاسیسات B", "name_en": "Facility B", "bunker_sheet_name": "بونکر B", "truck_destination": "مقصد B"},
    {"code": "C", "name_fa": "تاسیسات C", "name_en": "Facility C", "bunker_sheet_name": "بونکر C", "truck_destination": "مقصد C"},
]


@router.get("/")
def seed_data(db: Session = Depends(get_db)):
    allow_seed = os.getenv("ALLOW_SEED", "false").lower() == "true"
    if not allow_seed:
        return {"message": "Seed endpoint is disabled. Set ALLOW_SEED=true to enable."}

    seeded = {"drivers": 0, "trucks": 0, "facilities": 0}

    # Seed facilities
    for fac_data in FACILITIES:
        existing = db.query(Facility).filter(Facility.code == fac_data["code"]).first()
        if not existing:
            db.add(Facility(**fac_data))
            seeded["facilities"] += 1

    # Seed drivers
    for drv_data in DRIVERS:
        existing = db.query(Driver).filter(Driver.canonical_name == drv_data["canonical_name"]).first()
        if not existing:
            db.add(Driver(**drv_data))
            seeded["drivers"] += 1

    # Seed trucks
    for trk_data in TRUCKS:
        existing = db.query(Truck).filter(Truck.number == trk_data["number"]).first()
        if not existing:
            db.add(Truck(**trk_data))
            seeded["trucks"] += 1

    db.commit()
    return {"message": "Seed completed", "seeded": seeded}
