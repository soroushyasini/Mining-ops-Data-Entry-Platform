from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..database import get_db
from ..models import Shipment
from ..schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentRead
from ..services.bulk_import import preview_bulk_import

router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.get("/", response_model=List[ShipmentRead])
def list_shipments(
    skip: int = 0,
    limit: int = 200,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    facility_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    truck_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Shipment)
    if date_from:
        query = query.filter(Shipment.date >= date_from)
    if date_to:
        query = query.filter(Shipment.date <= date_to)
    if facility_id:
        query = query.filter(Shipment.facility_id == facility_id)
    if driver_id:
        query = query.filter(Shipment.driver_id == driver_id)
    if truck_id:
        query = query.filter(Shipment.truck_id == truck_id)
    return query.order_by(Shipment.date.desc()).offset(skip).limit(limit).all()


@router.get("/{shipment_id}", response_model=ShipmentRead)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="حمل یافت نشد")
    return shipment


@router.post("/", response_model=ShipmentRead, status_code=201)
def create_shipment(data: ShipmentCreate, db: Session = Depends(get_db)):
    shipment = Shipment(**data.model_dump())
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.put("/{shipment_id}", response_model=ShipmentRead)
def update_shipment(shipment_id: int, data: ShipmentUpdate, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="حمل یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(shipment, key, value)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.delete("/{shipment_id}", status_code=204)
def delete_shipment(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="حمل یافت نشد")
    db.delete(shipment)
    db.commit()


@router.post("/bulk-preview")
async def bulk_preview(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    return preview_bulk_import(contents, "shipment", db)


@router.post("/bulk-confirm")
def bulk_confirm(preview_data: Dict[str, Any], db: Session = Depends(get_db)):
    imported = 0
    skipped = 0
    for row in preview_data.get("rows", []):
        if row["status"] in ("valid", "warning"):
            data = row["data"]
            try:
                shipment = Shipment(
                    date=str(data.get("date", "")),
                    tonnage_kg=float(data.get("tonnage_kg", 0)),
                    receipt_number=data.get("receipt_number"),
                    destination=data.get("destination"),
                    notes=data.get("notes"),
                )
                db.add(shipment)
                imported += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    db.commit()
    return {"imported": imported, "skipped": skipped, "message": f"{imported} ردیف ثبت شد"}
