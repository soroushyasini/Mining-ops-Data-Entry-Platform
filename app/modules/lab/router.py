from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.lab import service
from app.modules.lab.schemas import (
    LabBatchCreate,
    LabBatchResponse,
    LabBatchUpdate,
    LabResultBulkCreate,
    LabResultCreate,
    LabResultResponse,
    LabResultUpdate,
)
from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import GrindingFacility, RecordStatus, SampleType
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()

# ---------------------------------------------------------------------------
# Batch endpoints  –  /api/v1/lab/batches
# ---------------------------------------------------------------------------

batches_router = APIRouter(prefix="/batches", tags=["lab-batches"])


def _batch_to_response(batch, results=None, attachments=None) -> LabBatchResponse:
    results = results or []
    attachments = attachments or []
    return LabBatchResponse(
        id=batch.id,
        issue_date_jalali=batch.issue_date_jalali,
        issue_date_gregorian=batch.issue_date_gregorian,
        analysis_count=batch.analysis_count,
        total_cost_rials=batch.total_cost_rials,
        status=batch.status,
        notes=batch.notes,
        created_at=batch.created_at,
        updated_at=batch.updated_at,
        results=[LabResultResponse.model_validate(r) for r in results],
        results_count=len(results),
        attachments=[AttachmentResponse.model_validate(a) for a in attachments],
    )


@batches_router.get("/", response_model=PaginatedResponse[LabBatchResponse])
async def list_batches(
    status: Optional[RecordStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    batches, total = await service.list_batches(
        db,
        pagination.page,
        pagination.size,
        status=status.value if status else None,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedResponse.create(
        items=[_batch_to_response(b) for b in batches],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@batches_router.get("/{batch_id}", response_model=LabBatchResponse)
async def get_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    batch, attachments = await service.get_batch_with_details(db, batch_id)
    return _batch_to_response(batch, results=batch.results, attachments=attachments)


@batches_router.post("/", response_model=LabBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(data: LabBatchCreate, db: AsyncSession = Depends(get_db)):
    batch = await service.create_batch(db, data)
    return _batch_to_response(batch)


@batches_router.put("/{batch_id}", response_model=LabBatchResponse)
async def update_batch(
    batch_id: int, data: LabBatchUpdate, db: AsyncSession = Depends(get_db)
):
    batch = await service.update_batch(db, batch_id, data)
    return _batch_to_response(batch)


@batches_router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(batch_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_batch(db, batch_id)


# ---------------------------------------------------------------------------
# Result endpoints  –  /api/v1/lab/results
# ---------------------------------------------------------------------------

results_router = APIRouter(prefix="/results", tags=["lab-results"])


@results_router.get("/", response_model=PaginatedResponse[LabResultResponse])
async def list_results(
    batch_id: Optional[int] = None,
    sample_type: Optional[SampleType] = None,
    source_facility: Optional[GrindingFacility] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    results, total = await service.list_results(
        db,
        pagination.page,
        pagination.size,
        batch_id=batch_id,
        sample_type=sample_type.value if sample_type else None,
        source_facility=source_facility.value if source_facility else None,
    )
    return PaginatedResponse.create(
        items=[LabResultResponse.model_validate(r) for r in results],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@results_router.get("/{result_id}", response_model=LabResultResponse)
async def get_result(result_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_result_or_404(db, result_id)


@results_router.post("/", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
async def create_result(
    batch_id: int,
    data: LabResultCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_result(db, batch_id, data)


@results_router.post("/bulk", response_model=list[LabResultResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_results(
    data: LabResultBulkCreate, db: AsyncSession = Depends(get_db)
):
    return await service.bulk_create_results(db, data.batch_id, data.results)


@results_router.put("/{result_id}", response_model=LabResultResponse)
async def update_result(
    result_id: int, data: LabResultUpdate, db: AsyncSession = Depends(get_db)
):
    return await service.update_result(db, result_id, data)


@results_router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_result(result_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_result(db, result_id)


# ---------------------------------------------------------------------------
# Compose into single lab router
# ---------------------------------------------------------------------------

router.include_router(batches_router)
router.include_router(results_router)
