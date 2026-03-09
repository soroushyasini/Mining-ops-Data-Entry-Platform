from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.lab.models import LabIssueBatch, LabResult
from app.modules.lab.schemas import (
    LabBatchCreate,
    LabBatchUpdate,
    LabResultCreate,
    LabResultUpdate,
)
from app.modules.attachments.models import Attachment
from app.shared.enums import EntityType, RecordStatus
from app.shared.exceptions import ConflictException, NotFoundException
from app.shared.jalali import jalali_to_gregorian
from app.shared.sample_parser import parse_sample_code


# ---------------------------------------------------------------------------
# Batch helpers
# ---------------------------------------------------------------------------

async def get_batch_or_404(db: AsyncSession, batch_id: int) -> LabIssueBatch:
    result = await db.execute(select(LabIssueBatch).where(LabIssueBatch.id == batch_id))
    batch = result.scalar_one_or_none()
    if not batch:
        raise NotFoundException(f"LabIssueBatch with id {batch_id} not found")
    return batch


async def list_batches(
    db: AsyncSession,
    page: int,
    size: int,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    query = select(LabIssueBatch)
    count_query = select(func.count(LabIssueBatch.id))

    if status:
        query = query.where(LabIssueBatch.status == status)
        count_query = count_query.where(LabIssueBatch.status == status)
    if date_from:
        greg_from = jalali_to_gregorian(date_from)
        query = query.where(LabIssueBatch.issue_date_gregorian >= greg_from)
        count_query = count_query.where(LabIssueBatch.issue_date_gregorian >= greg_from)
    if date_to:
        greg_to = jalali_to_gregorian(date_to)
        query = query.where(LabIssueBatch.issue_date_gregorian <= greg_to)
        count_query = count_query.where(LabIssueBatch.issue_date_gregorian <= greg_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(LabIssueBatch.id).offset((page - 1) * size).limit(size)
    )
    batches = result.scalars().all()
    return batches, total


async def get_batch_with_details(db: AsyncSession, batch_id: int):
    result = await db.execute(
        select(LabIssueBatch)
        .options(selectinload(LabIssueBatch.results))
        .where(LabIssueBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise NotFoundException(f"LabIssueBatch with id {batch_id} not found")

    attachments_result = await db.execute(
        select(Attachment).where(
            Attachment.entity_type == EntityType.LAB_BATCH.value,
            Attachment.entity_id == batch_id,
        )
    )
    attachments = attachments_result.scalars().all()
    return batch, list(attachments)


async def create_batch(db: AsyncSession, data: LabBatchCreate) -> LabIssueBatch:
    greg_date = jalali_to_gregorian(data.issue_date_jalali)

    existing = await db.execute(
        select(LabIssueBatch).where(LabIssueBatch.issue_date_jalali == data.issue_date_jalali)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(
            f"LabIssueBatch with issue_date_jalali '{data.issue_date_jalali}' already exists"
        )

    batch = LabIssueBatch(
        issue_date_jalali=data.issue_date_jalali,
        issue_date_gregorian=greg_date,
        notes=data.notes,
        status=RecordStatus.REGISTERED.value,
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    return batch


async def update_batch(db: AsyncSession, batch_id: int, data: LabBatchUpdate) -> LabIssueBatch:
    batch = await get_batch_or_404(db, batch_id)
    update_data = data.model_dump(exclude_unset=True)

    # Auto-transition: if analysis_count + total_cost_rials provided → "invoiced"
    adding_invoice = (
        "analysis_count" in update_data or "total_cost_rials" in update_data
    )
    if adding_invoice and batch.status == RecordStatus.REGISTERED.value:
        batch.status = RecordStatus.INVOICED.value

    if "status" in update_data:
        status_val = update_data.pop("status")
        batch.status = status_val.value if hasattr(status_val, "value") else status_val

    for key, value in update_data.items():
        setattr(batch, key, value)

    await db.commit()
    await db.refresh(batch)
    return batch


async def delete_batch(db: AsyncSession, batch_id: int) -> None:
    result = await db.execute(
        select(LabIssueBatch)
        .options(selectinload(LabIssueBatch.results))
        .where(LabIssueBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise NotFoundException(f"LabIssueBatch with id {batch_id} not found")

    if batch.status != RecordStatus.REGISTERED.value:
        raise ConflictException(
            f"Cannot delete LabIssueBatch with status '{batch.status}'. Only 'registered' batches can be deleted."
        )
    if batch.results:
        raise ConflictException(
            "Cannot delete LabIssueBatch that has lab results. Delete the results first."
        )

    await db.delete(batch)
    await db.commit()


# ---------------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------------

async def get_result_or_404(db: AsyncSession, result_id: int) -> LabResult:
    result = await db.execute(select(LabResult).where(LabResult.id == result_id))
    lab_result = result.scalar_one_or_none()
    if not lab_result:
        raise NotFoundException(f"LabResult with id {result_id} not found")
    return lab_result


async def list_results(
    db: AsyncSession,
    page: int,
    size: int,
    batch_id: Optional[int] = None,
    sample_type: Optional[str] = None,
    source_facility: Optional[str] = None,
):
    query = select(LabResult)
    count_query = select(func.count(LabResult.id))

    if batch_id is not None:
        query = query.where(LabResult.batch_id == batch_id)
        count_query = count_query.where(LabResult.batch_id == batch_id)
    if sample_type:
        query = query.where(LabResult.sample_type == sample_type)
        count_query = count_query.where(LabResult.sample_type == sample_type)
    if source_facility:
        query = query.where(LabResult.source_facility == source_facility)
        count_query = count_query.where(LabResult.source_facility == source_facility)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(LabResult.id).offset((page - 1) * size).limit(size)
    )
    results = result.scalars().all()
    return results, total


def _build_result_from_create(data: LabResultCreate, batch_id: int) -> LabResult:
    parsed = parse_sample_code(data.sample_code)
    sample_date_gregorian = None
    if parsed.get("sample_date_jalali"):
        try:
            sample_date_gregorian = jalali_to_gregorian(parsed["sample_date_jalali"])
        except ValueError:
            pass

    return LabResult(
        batch_id=batch_id,
        sample_code=data.sample_code,
        source_facility=parsed.get("source_facility"),
        sample_date_jalali=parsed.get("sample_date_jalali"),
        sample_date_gregorian=sample_date_gregorian,
        sample_type=parsed.get("sample_type"),
        sequence_number=parsed.get("sequence_number"),
        gold_ppm=data.gold_ppm,
    )


async def create_result(db: AsyncSession, batch_id: int, data: LabResultCreate) -> LabResult:
    # Ensure batch exists
    await get_batch_or_404(db, batch_id)

    existing = await db.execute(
        select(LabResult).where(LabResult.sample_code == data.sample_code)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(f"LabResult with sample_code '{data.sample_code}' already exists")

    lab_result = _build_result_from_create(data, batch_id)
    db.add(lab_result)
    await db.commit()
    await db.refresh(lab_result)
    return lab_result


async def bulk_create_results(
    db: AsyncSession, batch_id: int, results_data: List[LabResultCreate]
) -> List[LabResult]:
    # Ensure batch exists
    await get_batch_or_404(db, batch_id)

    # Check for duplicate sample codes in the incoming data
    codes = [r.sample_code for r in results_data]
    if len(codes) != len(set(codes)):
        raise ConflictException("Duplicate sample_code values in bulk create request")

    # Check against existing records
    existing = await db.execute(
        select(LabResult).where(LabResult.sample_code.in_(codes))
    )
    existing_codes = {r.sample_code for r in existing.scalars().all()}
    if existing_codes:
        raise ConflictException(
            f"sample_code(s) already exist: {', '.join(sorted(existing_codes))}"
        )

    lab_results = [_build_result_from_create(d, batch_id) for d in results_data]
    db.add_all(lab_results)
    await db.commit()
    for r in lab_results:
        await db.refresh(r)
    return lab_results


async def update_result(db: AsyncSession, result_id: int, data: LabResultUpdate) -> LabResult:
    lab_result = await get_result_or_404(db, result_id)
    update_data = data.model_dump(exclude_unset=True)

    if "sample_code" in update_data:
        new_code = update_data["sample_code"]
        if new_code != lab_result.sample_code:
            existing = await db.execute(
                select(LabResult).where(
                    LabResult.sample_code == new_code,
                    LabResult.id != result_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictException(
                    f"LabResult with sample_code '{new_code}' already exists"
                )
        # Re-parse
        parsed = parse_sample_code(new_code)
        lab_result.sample_code = new_code
        lab_result.source_facility = parsed.get("source_facility")
        lab_result.sample_date_jalali = parsed.get("sample_date_jalali")
        lab_result.sample_type = parsed.get("sample_type")
        lab_result.sequence_number = parsed.get("sequence_number")
        if parsed.get("sample_date_jalali"):
            try:
                lab_result.sample_date_gregorian = jalali_to_gregorian(parsed["sample_date_jalali"])
            except ValueError:
                lab_result.sample_date_gregorian = None
        else:
            lab_result.sample_date_gregorian = None
        update_data.pop("sample_code")

    for key, value in update_data.items():
        setattr(lab_result, key, value)

    await db.commit()
    await db.refresh(lab_result)
    return lab_result


async def delete_result(db: AsyncSession, result_id: int) -> None:
    lab_result = await get_result_or_404(db, result_id)
    await db.delete(lab_result)
    await db.commit()
