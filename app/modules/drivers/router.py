from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.drivers import service
from app.modules.drivers.schemas import DriverCreate, DriverResponse, DriverUpdate
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[DriverResponse])
async def list_drivers(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    drivers, total = await service.list_drivers(db, pagination.page, pagination.size)
    return PaginatedResponse.create(
        items=[DriverResponse.model_validate(d) for d in drivers],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_driver_or_404(db, driver_id)


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(data: DriverCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_driver(db, data)


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: int, data: DriverUpdate, db: AsyncSession = Depends(get_db)
):
    return await service.update_driver(db, driver_id, data)


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(driver_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_driver(db, driver_id)
