from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.trucks import service
from app.modules.trucks.schemas import (
    TruckLoadCreate,
    TruckLoadResponse,
    TruckLoadUpdate,
    TruckStatusPatch,
)
from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import GrindingFacility, RecordStatus
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TruckLoadResponse])
async def list_trucks(
    status: Optional[RecordStatus] = None,
    destination: Optional[GrindingFacility] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    trucks, total = await service.list_trucks(
        db,
        pagination.page,
        pagination.size,
        status=status.value if status else None,
        destination=destination.value if destination else None,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedResponse.create(
        items=[TruckLoadResponse.model_validate(t) for t in trucks],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{truck_id}", response_model=TruckLoadResponse)
async def get_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    truck, attachments = await service.get_truck_with_attachments(db, truck_id)
    response = TruckLoadResponse.model_validate(truck)
    response.attachments = [AttachmentResponse.model_validate(a) for a in attachments]
    return response


@router.post("/", response_model=TruckLoadResponse, status_code=status.HTTP_201_CREATED)
async def create_truck(data: TruckLoadCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_truck(db, data)


@router.put("/{truck_id}", response_model=TruckLoadResponse)
async def update_truck(
    truck_id: int, data: TruckLoadUpdate, db: AsyncSession = Depends(get_db)
):
    return await service.update_truck(db, truck_id, data)


@router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_truck(truck_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_truck(db, truck_id)


@router.patch("/{truck_id}/status", response_model=TruckLoadResponse)
async def patch_truck_status(
    truck_id: int, data: TruckStatusPatch, db: AsyncSession = Depends(get_db)
):
    return await service.patch_truck_status(db, truck_id, data)
