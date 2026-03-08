from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.drivers.models import Driver
from app.modules.drivers.schemas import DriverCreate, DriverUpdate
from app.modules.cars.models import Car
from app.modules.trucks.models import TruckLoad
from app.shared.exceptions import ConflictException, NotFoundException


async def get_driver_or_404(db: AsyncSession, driver_id: int) -> Driver:
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise NotFoundException(f"Driver with id {driver_id} not found")
    return driver


async def list_drivers(db: AsyncSession, page: int, size: int):
    total_result = await db.execute(select(func.count(Driver.id)))
    total = total_result.scalar_one()

    result = await db.execute(
        select(Driver).order_by(Driver.id).offset((page - 1) * size).limit(size)
    )
    drivers = result.scalars().all()
    return drivers, total


async def create_driver(db: AsyncSession, data: DriverCreate) -> Driver:
    driver = Driver(**data.model_dump())
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return driver


async def update_driver(db: AsyncSession, driver_id: int, data: DriverUpdate) -> Driver:
    driver = await get_driver_or_404(db, driver_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(driver, key, value)
    await db.commit()
    await db.refresh(driver)
    return driver


async def delete_driver(db: AsyncSession, driver_id: int) -> None:
    driver = await get_driver_or_404(db, driver_id)

    # Check if referenced by cars
    car_result = await db.execute(
        select(Car).where(Car.current_driver_id == driver_id).limit(1)
    )
    if car_result.scalar_one_or_none():
        raise ConflictException("Driver is referenced by one or more cars")

    # Check if referenced by trucks (by name — informational only, not enforced)
    await db.delete(driver)
    await db.commit()
