from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Truck
from ..schemas.truck import TruckCreate, TruckUpdate, TruckRead

router = APIRouter(prefix="/trucks", tags=["trucks"])


@router.get("/", response_model=List[TruckRead])
def list_trucks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Truck).offset(skip).limit(limit).all()


@router.get("/{truck_id}", response_model=TruckRead)
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="کامیون یافت نشد")
    return truck


@router.post("/", response_model=TruckRead, status_code=201)
def create_truck(data: TruckCreate, db: Session = Depends(get_db)):
    truck = Truck(**data.model_dump())
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


@router.put("/{truck_id}", response_model=TruckRead)
def update_truck(truck_id: int, data: TruckUpdate, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="کامیون یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(truck, key, value)
    db.commit()
    db.refresh(truck)
    return truck


@router.delete("/{truck_id}", status_code=204)
def delete_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="کامیون یافت نشد")
    db.delete(truck)
    db.commit()
