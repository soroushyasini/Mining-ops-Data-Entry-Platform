from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..database import get_db
from ..models import LabSample
from ..schemas.lab_sample import LabSampleCreate, LabSampleUpdate, LabSampleRead
from ..services.bulk_import import preview_bulk_import

router = APIRouter(prefix="/lab-samples", tags=["lab_samples"])


@router.get("/", response_model=List[LabSampleRead])
def list_lab_samples(
    skip: int = 0,
    limit: int = 200,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    facility_id: Optional[int] = None,
    sample_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LabSample)
    if date_from:
        query = query.filter(LabSample.date >= date_from)
    if date_to:
        query = query.filter(LabSample.date <= date_to)
    if facility_id:
        query = query.filter(LabSample.facility_id == facility_id)
    if sample_type:
        query = query.filter(LabSample.sample_type == sample_type)
    return query.order_by(LabSample.id.desc()).offset(skip).limit(limit).all()


@router.get("/{record_id}", response_model=LabSampleRead)
def get_lab_sample(record_id: int, db: Session = Depends(get_db)):
    record = db.query(LabSample).filter(LabSample.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="نمونه آزمایشگاه یافت نشد")
    return record


@router.post("/", response_model=LabSampleRead, status_code=201)
def create_lab_sample(data: LabSampleCreate, db: Session = Depends(get_db)):
    record = LabSample(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=LabSampleRead)
def update_lab_sample(record_id: int, data: LabSampleUpdate, db: Session = Depends(get_db)):
    record = db.query(LabSample).filter(LabSample.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="نمونه آزمایشگاه یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_lab_sample(record_id: int, db: Session = Depends(get_db)):
    record = db.query(LabSample).filter(LabSample.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="نمونه آزمایشگاه یافت نشد")
    db.delete(record)
    db.commit()


@router.post("/bulk-preview")
async def bulk_preview(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    return preview_bulk_import(contents, "lab_sample", db)


@router.post("/bulk-confirm")
def bulk_confirm(preview_data: Dict[str, Any], db: Session = Depends(get_db)):
    imported = 0
    skipped = 0
    for row in preview_data.get("rows", []):
        if row["status"] in ("valid", "warning"):
            data = row["data"]
            try:
                record = LabSample(
                    sample_code=str(data.get("sample_code", "")),
                    sheet_name=str(data.get("sheet_name", "")),
                    au_ppm=data.get("au_ppm"),
                )
                db.add(record)
                imported += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    db.commit()
    return {"imported": imported, "skipped": skipped, "message": f"{imported} ردیف ثبت شد"}
