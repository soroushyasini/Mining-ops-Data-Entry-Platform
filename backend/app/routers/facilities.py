from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Facility
from ..schemas.facility import FacilityCreate, FacilityUpdate, FacilityRead

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.get("/", response_model=List[FacilityRead])
def list_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Facility).offset(skip).limit(limit).all()


@router.get("/{facility_id}", response_model=FacilityRead)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="تاسیسات یافت نشد")
    return facility


@router.post("/", response_model=FacilityRead, status_code=201)
def create_facility(data: FacilityCreate, db: Session = Depends(get_db)):
    facility = Facility(**data.model_dump())
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility


@router.put("/{facility_id}", response_model=FacilityRead)
def update_facility(facility_id: int, data: FacilityUpdate, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="تاسیسات یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(facility, key, value)
    db.commit()
    db.refresh(facility)
    return facility


@router.delete("/{facility_id}", status_code=204)
def delete_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="تاسیسات یافت نشد")
    db.delete(facility)
    db.commit()
