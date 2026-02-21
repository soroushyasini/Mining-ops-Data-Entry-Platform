from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Payment
from ..schemas.payment import PaymentCreate, PaymentUpdate, PaymentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=List[PaymentRead])
def list_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Payment).order_by(Payment.id.desc()).offset(skip).limit(limit).all()


@router.get("/{record_id}", response_model=PaymentRead)
def get_payment(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="پرداخت یافت نشد")
    return record


@router.post("/", response_model=PaymentRead, status_code=201)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    record = Payment(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=PaymentRead)
def update_payment(record_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="پرداخت یافت نشد")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_payment(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="پرداخت یافت نشد")
    db.delete(record)
    db.commit()
