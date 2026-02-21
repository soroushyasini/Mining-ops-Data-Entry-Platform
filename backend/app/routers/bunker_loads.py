from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models import BunkerLoad
from ..schemas.bunker_load import BunkerLoadCreate, BunkerLoadUpdate, BunkerLoadRead
from ..services.bulk_import import preview_bulk_import

router = APIRouter(prefix="/bunker-loads", tags=["bunker_loads"])


@router.get("/", response_model=List[BunkerLoadRead])
def list_bunker_loads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(BunkerLoad).order_by(BunkerLoad.id.desc()).offset(skip).limit(limit).all()


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
                    sheet_name=data.get("sheet_name"),
                )
                db.add(record)
                imported += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    db.commit()
    return {"imported": imported, "skipped": skipped, "message": f"{imported} ردیف ثبت شد"}
