from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.grinding.models import GrindingLedgerEntry
from app.modules.grinding.schemas import GrindingCreate, GrindingUpdate
from app.modules.attachments.models import Attachment
from app.shared.enums import EntityType, RecordStatus
from app.shared.exceptions import ConflictException, NotFoundException
from app.shared.jalali import jalali_to_gregorian


async def get_grinding_or_404(db: AsyncSession, entry_id: int) -> GrindingLedgerEntry:
    result = await db.execute(
        select(GrindingLedgerEntry).where(GrindingLedgerEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise NotFoundException(f"GrindingLedgerEntry with id {entry_id} not found")
    return entry


async def list_grinding_entries(
    db: AsyncSession,
    page: int,
    size: int,
    status: Optional[str] = None,
    facility: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    query = select(GrindingLedgerEntry)
    count_query = select(func.count(GrindingLedgerEntry.id))

    if status:
        query = query.where(GrindingLedgerEntry.status == status)
        count_query = count_query.where(GrindingLedgerEntry.status == status)
    if facility:
        query = query.where(GrindingLedgerEntry.facility == facility)
        count_query = count_query.where(GrindingLedgerEntry.facility == facility)
    if date_from:
        greg_from = jalali_to_gregorian(date_from)
        query = query.where(GrindingLedgerEntry.date_gregorian >= greg_from)
        count_query = count_query.where(GrindingLedgerEntry.date_gregorian >= greg_from)
    if date_to:
        greg_to = jalali_to_gregorian(date_to)
        query = query.where(GrindingLedgerEntry.date_gregorian <= greg_to)
        count_query = count_query.where(GrindingLedgerEntry.date_gregorian <= greg_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(GrindingLedgerEntry.id).offset((page - 1) * size).limit(size)
    )
    entries = result.scalars().all()
    return entries, total


async def get_grinding_with_attachments(db: AsyncSession, entry_id: int):
    entry = await get_grinding_or_404(db, entry_id)
    attachments_result = await db.execute(
        select(Attachment).where(
            Attachment.entity_type == EntityType.GRINDING.value,
            Attachment.entity_id == entry_id,
        )
    )
    attachments = attachments_result.scalars().all()
    return entry, list(attachments)


async def create_grinding_entry(
    db: AsyncSession, data: GrindingCreate
) -> GrindingLedgerEntry:
    greg_date = jalali_to_gregorian(data.date_jalali)

    if data.receipt_number is not None:
        existing = await db.execute(
            select(GrindingLedgerEntry).where(
                GrindingLedgerEntry.receipt_number == data.receipt_number
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException(
                f"GrindingLedgerEntry with receipt_number {data.receipt_number} already exists"
            )

    dump = data.model_dump()
    dump["facility"] = dump["facility"].value if hasattr(dump["facility"], "value") else dump["facility"]
    dump.pop("date_jalali")
    entry = GrindingLedgerEntry(
        **dump,
        date_jalali=data.date_jalali,
        date_gregorian=greg_date,
        status=RecordStatus.REGISTERED.value,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def update_grinding_entry(
    db: AsyncSession, entry_id: int, data: GrindingUpdate
) -> GrindingLedgerEntry:
    entry = await get_grinding_or_404(db, entry_id)
    update_data = data.model_dump(exclude_unset=True)

    if "date_jalali" in update_data:
        entry.date_gregorian = jalali_to_gregorian(update_data["date_jalali"])

    if "receipt_number" in update_data and update_data["receipt_number"] is not None:
        if update_data["receipt_number"] != entry.receipt_number:
            existing = await db.execute(
                select(GrindingLedgerEntry).where(
                    GrindingLedgerEntry.receipt_number == update_data["receipt_number"],
                    GrindingLedgerEntry.id != entry_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictException(
                    f"GrindingLedgerEntry with receipt_number {update_data['receipt_number']} already exists"
                )

    # Auto-transition: if cost fields provided to "registered" record → "costed"
    adding_cost = (
        "grinding_cost_rials" in update_data or "total_cost_rials" in update_data
    )
    if adding_cost and entry.status == RecordStatus.REGISTERED.value:
        entry.status = RecordStatus.COSTED.value

    if "facility" in update_data:
        fac = update_data["facility"]
        update_data["facility"] = fac.value if hasattr(fac, "value") else fac

    for key, value in update_data.items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)
    return entry


async def delete_grinding_entry(db: AsyncSession, entry_id: int) -> None:
    entry = await get_grinding_or_404(db, entry_id)
    if entry.status != RecordStatus.REGISTERED.value:
        raise ConflictException(
            f"Cannot delete GrindingLedgerEntry with status '{entry.status}'. Only 'registered' records can be deleted."
        )
    await db.delete(entry)
    await db.commit()
