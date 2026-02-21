from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..database import get_db
from ..models import BunkerLoad
from ..schemas.bunker_load import BunkerLoadCreate, BunkerLoadUpdate, BunkerLoadRead
from ..services.bulk_import import preview_bulk_import

router = APIRouter(prefix="/bunker-loads", tags=["bunker_loads"])


@router.get("/stats/summary")
def bunker_loads_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    facility_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Returns total tonnage, total cost, record count for the filtered period.
    Supports filters: date_from, date_to, facility_id."""
    query = db.query(BunkerLoad)
    if date_from:
        query = query.filter(BunkerLoad.date >= date_from)
    if date_to:
        query = query.filter(BunkerLoad.date <= date_to)
    if facility_id:
        query = query.filter(BunkerLoad.facility_id == facility_id)

    records = query.all()
    total_tonnage = sum(r.tonnage_kg for r in records if r.tonnage_kg)
    total_cost = sum(r.total_cost_rial for r in records if r.total_cost_rial)

    return {
        "count": len(records),
        "total_tonnage_kg": total_tonnage,
        "total_cost_rial": total_cost
    }


@router.get("/", response_model=List[BunkerLoadRead])
def list_bunker_loads(
    skip: int = 0,
    limit: int = 200,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    facility_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(BunkerLoad)
    if date_from:
        query = query.filter(BunkerLoad.date >= date_from)
    if date_to:
        query = query.filter(BunkerLoad.date <= date_to)
    if facility_id:
        query = query.filter(BunkerLoad.facility_id == facility_id)
    if driver_id:
        query = query.filter(BunkerLoad.driver_id == driver_id)
    return query.order_by(BunkerLoad.date.desc()).offset(skip).limit(limit).all()


@router.get("/{record_id}", response_model=BunkerLoadRead)
def get_bunker_load(record_id: int, db: Session = Depends(get_db)):
    record = db.query(BunkerLoad).filter(BunkerLoad.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="بارگیری بونکر یافت نشد")
    return record


@router.post("/", response_model=BunkerLoadRead, status_code=201)
def create_bunker_load(data: BunkerLoadCreate, db: Session = Depends(get_db)):
    record = BunkerLoad(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=BunkerLoadRead)
def update_bunker_load(record_id: int, data: BunkerLoadUpdate, db: Session = Depends(get_db)):
    record = db.query(BunkerLoad).filter(BunkerLoad.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="بارگیری بونکر یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_bunker_load(record_id: int, db: Session = Depends(get_db)):
    record = db.query(BunkerLoad).filter(BunkerLoad.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="بارگیری بونکر یافت نشد")
    db.delete(record)
    db.commit()


@router.post("/excel-headers")
async def excel_headers(file: UploadFile = File(...)):
    """Read and return the column headers from an uploaded Excel file."""
    contents = await file.read()
    try:
        import openpyxl
        import io
        wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True, read_only=True)
        ws = wb.active
        first_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), [])
        headers = [str(h).strip() if h is not None else "" for h in first_row]
        return {"headers": headers}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطا در خواندن فایل: {str(e)}")


@router.post("/bulk-preview")
async def bulk_preview(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    return preview_bulk_import(contents, "bunker_load", db)


@router.post("/bulk-confirm")
def bulk_confirm(preview_data: Dict[str, Any], db: Session = Depends(get_db)):
    imported = 0
    skipped = 0
    for row in preview_data.get("rows", []):
        if row["status"] in ("valid", "warning"):
            data = row["data"]
            try:
                record = BunkerLoad(
                    date=str(data.get("date", "")),
                    tonnage_kg=float(data.get("tonnage_kg", 0)),
                    time=data.get("time"),
                    truck_number_raw=data.get("truck_number_raw"),
                    receipt_number=data.get("receipt_number"),
                    origin=data.get("origin"),
                    cost_per_ton_rial=data.get("cost_per_ton_rial"),
                    total_cost_rial=data.get("total_cost_rial"),
                    notes=data.get("notes"),
                    driver_id=data.get("driver_id"),
                    facility_id=data.get("facility_id"),
                )
                db.add(record)
                imported += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    db.commit()
    return {"imported": imported, "skipped": skipped, "message": f"{imported} ردیف ثبت شد"}
