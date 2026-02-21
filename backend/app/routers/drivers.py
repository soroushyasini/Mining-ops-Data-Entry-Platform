from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Driver
from ..schemas.driver import DriverCreate, DriverUpdate, DriverRead

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("/", response_model=List[DriverRead])
def list_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Driver).offset(skip).limit(limit).all()


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="راننده یافت نشد")
    return driver


@router.post("/", response_model=DriverRead, status_code=201)
def create_driver(data: DriverCreate, db: Session = Depends(get_db)):
    driver = Driver(**data.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(driver_id: int, data: DriverUpdate, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="راننده یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(driver, key, value)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=204)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="راننده یافت نشد")
    db.delete(driver)
    db.commit()
