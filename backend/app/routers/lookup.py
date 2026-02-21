from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.lookup import lookup_by_truck_number

router = APIRouter(prefix="/lookup", tags=["lookup"])


@router.get("/truck/{truck_number}")
def lookup_truck(truck_number: str, db: Session = Depends(get_db)):
    result = lookup_by_truck_number(truck_number, db)
    return result
