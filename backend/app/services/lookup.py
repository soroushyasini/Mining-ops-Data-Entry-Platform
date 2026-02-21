from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..models import Truck, Driver, Facility, Shipment, TransportCost


class LookupResult(BaseModel):
    truck: Optional[dict] = None
    driver: Optional[dict] = None
    facility: Optional[dict] = None
    cost_per_ton_rial: Optional[float] = None
    found: bool = False


def mask_bank_account(account: Optional[str]) -> Optional[str]:
    """Partially mask a bank account number, showing only prefix and last 4 digits."""
    if not account:
        return None
    if len(account) <= 6:
        return account
    return account[:2] + "..." + account[-4:]


def lookup_by_truck_number(truck_number: str, db: Session) -> LookupResult:
    """
    Given a truck number:
    1. Find the Truck record
    2. Find Shipments for this truck to determine the usual facility
    3. Find the Driver associated with most recent shipments for this truck
    4. Find the active TransportCost rate for the identified route
    Returns: LookupResult with truck, driver, facility, cost_per_ton
    """
    truck = db.query(Truck).filter(Truck.number == truck_number).first()
    if not truck:
        return LookupResult(found=False)

    # Find most recent shipment for this truck to determine driver and facility
    recent_shipment = (
        db.query(Shipment)
        .filter(Shipment.truck_id == truck.id)
        .order_by(Shipment.id.desc())
        .first()
    )

    driver = None
    facility = None
    cost_per_ton = None

    if recent_shipment:
        if recent_shipment.driver_id:
            driver = db.query(Driver).filter(Driver.id == recent_shipment.driver_id).first()
        if recent_shipment.facility_id:
            facility = db.query(Facility).filter(Facility.id == recent_shipment.facility_id).first()

    # Try to find active transport cost for the facility
    if facility:
        tc = (
            db.query(TransportCost)
            .filter(TransportCost.facility_id == facility.id)
            .order_by(TransportCost.id.desc())
            .first()
        )
        if tc:
            cost_per_ton = tc.cost_per_ton_rial

    truck_dict = {"id": truck.id, "number": truck.number, "status": truck.status}
    driver_dict = None
    if driver:
        driver_dict = {
            "id": driver.id,
            "canonical_name": driver.canonical_name,
            "bank_account": mask_bank_account(driver.bank_account),
            "phone": driver.phone,
            "status": driver.status,
        }
    facility_dict = None
    if facility:
        facility_dict = {
            "id": facility.id,
            "code": facility.code,
            "name_fa": facility.name_fa,
            "name_en": facility.name_en,
            "truck_destination": facility.truck_destination,
        }

    return LookupResult(
        truck=truck_dict,
        driver=driver_dict,
        facility=facility_dict,
        cost_per_ton_rial=cost_per_ton,
        found=True,
    )
