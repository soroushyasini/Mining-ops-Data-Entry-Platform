from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.cars import service
from app.modules.cars.schemas import CarCreate, CarResponse, CarUpdate
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CarResponse])
async def list_cars(
    driver_id: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    cars, total = await service.list_cars(db, pagination.page, pagination.size, driver_id)
    return PaginatedResponse.create(
        items=[CarResponse.model_validate(c) for c in cars],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(car_id: int, db: AsyncSession = Depends(get_db)):
    car = await service.get_car_or_404(db, car_id)
    return CarResponse.model_validate(car)


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(data: CarCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_car(db, data)


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(car_id: int, data: CarUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_car(db, car_id, data)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_car(db, car_id)
