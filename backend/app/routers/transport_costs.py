from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import TransportCost
from ..schemas.transport_cost import TransportCostCreate, TransportCostUpdate, TransportCostRead

router = APIRouter(prefix="/transport-costs", tags=["transport_costs"])


@router.get("/", response_model=List[TransportCostRead])
def list_transport_costs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TransportCost).order_by(TransportCost.id.desc()).offset(skip).limit(limit).all()


@router.get("/{record_id}", response_model=TransportCostRead)
def get_transport_cost(record_id: int, db: Session = Depends(get_db)):
    record = db.query(TransportCost).filter(TransportCost.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="نرخ حمل یافت نشد")
    return record


@router.post("/", response_model=TransportCostRead, status_code=201)
def create_transport_cost(data: TransportCostCreate, db: Session = Depends(get_db)):
    record = TransportCost(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=TransportCostRead)
def update_transport_cost(record_id: int, data: TransportCostUpdate, db: Session = Depends(get_db)):
    record = db.query(TransportCost).filter(TransportCost.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="نرخ حمل یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_transport_cost(record_id: int, db: Session = Depends(get_db)):
    record = db.query(TransportCost).filter(TransportCost.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="نرخ حمل یافت نشد")
    db.delete(record)
    db.commit()
