from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.grinding import service
from app.modules.grinding.schemas import GrindingCreate, GrindingResponse, GrindingUpdate
from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import GrindingFacility, RecordStatus
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[GrindingResponse])
async def list_grinding_entries(
    status: Optional[RecordStatus] = None,
    facility: Optional[GrindingFacility] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    entries, total = await service.list_grinding_entries(
        db,
        pagination.page,
        pagination.size,
        status=status.value if status else None,
        facility=facility.value if facility else None,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedResponse.create(
        items=[GrindingResponse.model_validate(e) for e in entries],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{entry_id}", response_model=GrindingResponse)
async def get_grinding_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    entry, attachments = await service.get_grinding_with_attachments(db, entry_id)
    response = GrindingResponse.model_validate(entry)
    response.attachments = [AttachmentResponse.model_validate(a) for a in attachments]
    return response


@router.post("/", response_model=GrindingResponse, status_code=status.HTTP_201_CREATED)
async def create_grinding_entry(data: GrindingCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_grinding_entry(db, data)


@router.put("/{entry_id}", response_model=GrindingResponse)
async def update_grinding_entry(
    entry_id: int, data: GrindingUpdate, db: AsyncSession = Depends(get_db)
):
    return await service.update_grinding_entry(db, entry_id, data)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grinding_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_grinding_entry(db, entry_id)
