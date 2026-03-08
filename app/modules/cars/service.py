from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cars.models import Car
from app.modules.cars.schemas import CarCreate, CarUpdate
from app.shared.exceptions import ConflictException, NotFoundException


async def get_car_or_404(db: AsyncSession, car_id: int) -> Car:
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise NotFoundException(f"Car with id {car_id} not found")
    return car


async def list_cars(
    db: AsyncSession,
    page: int,
    size: int,
    driver_id: Optional[int] = None,
):
    query = select(Car)
    count_query = select(func.count(Car.id))

    if driver_id is not None:
        query = query.where(Car.current_driver_id == driver_id)
        count_query = count_query.where(Car.current_driver_id == driver_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(Car.id).offset((page - 1) * size).limit(size)
    )
    cars = result.scalars().all()
    return cars, total


async def create_car(db: AsyncSession, data: CarCreate) -> Car:
    existing = await db.execute(
        select(Car).where(Car.plate_number == data.plate_number)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(f"Car with plate_number '{data.plate_number}' already exists")

    car = Car(**data.model_dump())
    db.add(car)
    await db.commit()
    await db.refresh(car)
    return car


async def update_car(db: AsyncSession, car_id: int, data: CarUpdate) -> Car:
    car = await get_car_or_404(db, car_id)

    update_data = data.model_dump(exclude_unset=True)

    if "plate_number" in update_data:
        existing = await db.execute(
            select(Car).where(
                Car.plate_number == update_data["plate_number"],
                Car.id != car_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException(
                f"Car with plate_number '{update_data['plate_number']}' already exists"
            )

    for key, value in update_data.items():
        setattr(car, key, value)

    await db.commit()
    await db.refresh(car)
    return car


async def delete_car(db: AsyncSession, car_id: int) -> None:
    car = await get_car_or_404(db, car_id)
    await db.delete(car)
    await db.commit()
