from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.bunkers import service
from app.modules.bunkers.schemas import BunkerCreate, BunkerResponse, BunkerUpdate
from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import GrindingFacility, RecordStatus
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[BunkerResponse])
async def list_bunkers(
    status: Optional[RecordStatus] = None,
    source_facility: Optional[GrindingFacility] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    bunkers, total = await service.list_bunkers(
        db,
        pagination.page,
        pagination.size,
        status=status.value if status else None,
        source_facility=source_facility.value if source_facility else None,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedResponse.create(
        items=[BunkerResponse.model_validate(b) for b in bunkers],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{bunker_id}", response_model=BunkerResponse)
async def get_bunker(bunker_id: int, db: AsyncSession = Depends(get_db)):
    bunker, attachments = await service.get_bunker_with_attachments(db, bunker_id)
    response = BunkerResponse.model_validate(bunker)
    response.attachments = [AttachmentResponse.model_validate(a) for a in attachments]
    return response


@router.post("/", response_model=BunkerResponse, status_code=status.HTTP_201_CREATED)
async def create_bunker(data: BunkerCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_bunker(db, data)


@router.put("/{bunker_id}", response_model=BunkerResponse)
async def update_bunker(
    bunker_id: int, data: BunkerUpdate, db: AsyncSession = Depends(get_db)
):
    return await service.update_bunker(db, bunker_id, data)


@router.delete("/{bunker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bunker(bunker_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_bunker(db, bunker_id)
