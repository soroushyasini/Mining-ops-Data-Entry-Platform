from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bunkers.models import BunkerLoad
from app.modules.bunkers.schemas import BunkerCreate, BunkerUpdate
from app.modules.attachments.models import Attachment
from app.shared.enums import EntityType, RecordStatus
from app.shared.exceptions import ConflictException, NotFoundException
from app.shared.jalali import jalali_to_gregorian


async def get_bunker_or_404(db: AsyncSession, bunker_id: int) -> BunkerLoad:
    result = await db.execute(select(BunkerLoad).where(BunkerLoad.id == bunker_id))
    bunker = result.scalar_one_or_none()
    if not bunker:
        raise NotFoundException(f"BunkerLoad with id {bunker_id} not found")
    return bunker


async def list_bunkers(
    db: AsyncSession,
    page: int,
    size: int,
    status: Optional[str] = None,
    source_facility: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    query = select(BunkerLoad)
    count_query = select(func.count(BunkerLoad.id))

    if status:
        query = query.where(BunkerLoad.status == status)
        count_query = count_query.where(BunkerLoad.status == status)
    if source_facility:
        query = query.where(BunkerLoad.source_facility == source_facility)
        count_query = count_query.where(BunkerLoad.source_facility == source_facility)
    if date_from:
        greg_from = jalali_to_gregorian(date_from)
        query = query.where(BunkerLoad.date_gregorian >= greg_from)
        count_query = count_query.where(BunkerLoad.date_gregorian >= greg_from)
    if date_to:
        greg_to = jalali_to_gregorian(date_to)
        query = query.where(BunkerLoad.date_gregorian <= greg_to)
        count_query = count_query.where(BunkerLoad.date_gregorian <= greg_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(BunkerLoad.id).offset((page - 1) * size).limit(size)
    )
    bunkers = result.scalars().all()
    return bunkers, total


async def get_bunker_with_attachments(db: AsyncSession, bunker_id: int):
    bunker = await get_bunker_or_404(db, bunker_id)
    attachments_result = await db.execute(
        select(Attachment).where(
            Attachment.entity_type == EntityType.BUNKER.value,
            Attachment.entity_id == bunker_id,
        )
    )
    attachments = attachments_result.scalars().all()
    return bunker, list(attachments)


async def create_bunker(db: AsyncSession, data: BunkerCreate) -> BunkerLoad:
    greg_date = jalali_to_gregorian(data.date_jalali)

    existing = await db.execute(
        select(BunkerLoad).where(BunkerLoad.receipt_number == data.receipt_number)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(
            f"BunkerLoad with receipt_number {data.receipt_number} already exists"
        )

    dump = data.model_dump()
    dump["source_facility"] = dump["source_facility"].value if hasattr(dump["source_facility"], "value") else dump["source_facility"]
    dump.pop("date_jalali")
    bunker = BunkerLoad(
        **dump,
        date_jalali=data.date_jalali,
        date_gregorian=greg_date,
        status=RecordStatus.REGISTERED.value,
    )
    db.add(bunker)
    await db.commit()
    await db.refresh(bunker)
    return bunker


async def update_bunker(db: AsyncSession, bunker_id: int, data: BunkerUpdate) -> BunkerLoad:
    bunker = await get_bunker_or_404(db, bunker_id)
    update_data = data.model_dump(exclude_unset=True)

    if "date_jalali" in update_data:
        bunker.date_gregorian = jalali_to_gregorian(update_data["date_jalali"])

    if "receipt_number" in update_data and update_data["receipt_number"] != bunker.receipt_number:
        existing = await db.execute(
            select(BunkerLoad).where(
                BunkerLoad.receipt_number == update_data["receipt_number"],
                BunkerLoad.id != bunker_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException(
                f"BunkerLoad with receipt_number {update_data['receipt_number']} already exists"
            )

    # Auto-transition: if cost fields are added to a "registered" record → "costed"
    adding_cost = (
        "cost_per_ton_rials" in update_data or "total_cost_rials" in update_data
    )
    if adding_cost and bunker.status == RecordStatus.REGISTERED.value:
        bunker.status = RecordStatus.COSTED.value

    if "source_facility" in update_data:
        sf = update_data["source_facility"]
        update_data["source_facility"] = sf.value if hasattr(sf, "value") else sf

    for key, value in update_data.items():
        setattr(bunker, key, value)

    await db.commit()
    await db.refresh(bunker)
    return bunker


async def delete_bunker(db: AsyncSession, bunker_id: int) -> None:
    bunker = await get_bunker_or_404(db, bunker_id)
    if bunker.status != RecordStatus.REGISTERED.value:
        raise ConflictException(
            f"Cannot delete BunkerLoad with status '{bunker.status}'. Only 'registered' records can be deleted."
        )
    await db.delete(bunker)
    await db.commit()
