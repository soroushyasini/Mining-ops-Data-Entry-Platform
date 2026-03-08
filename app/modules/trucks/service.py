from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.trucks.models import TruckLoad
from app.modules.trucks.schemas import TruckLoadCreate, TruckLoadUpdate, TruckStatusPatch
from app.modules.attachments.models import Attachment
from app.shared.enums import EntityType, RecordStatus
from app.shared.exceptions import BadRequestException, ConflictException, NotFoundException
from app.shared.jalali import jalali_to_gregorian

# Status transition order
STATUS_ORDER = {
    RecordStatus.REGISTERED: 0,
    RecordStatus.COSTED: 1,
    RecordStatus.PAID: 2,
}


async def get_truck_or_404(db: AsyncSession, truck_id: int) -> TruckLoad:
    result = await db.execute(select(TruckLoad).where(TruckLoad.id == truck_id))
    truck = result.scalar_one_or_none()
    if not truck:
        raise NotFoundException(f"TruckLoad with id {truck_id} not found")
    return truck


async def list_trucks(
    db: AsyncSession,
    page: int,
    size: int,
    status: Optional[str] = None,
    destination: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    query = select(TruckLoad)
    count_query = select(func.count(TruckLoad.id))

    if status:
        query = query.where(TruckLoad.status == status)
        count_query = count_query.where(TruckLoad.status == status)
    if destination:
        query = query.where(TruckLoad.destination == destination)
        count_query = count_query.where(TruckLoad.destination == destination)
    if date_from:
        greg_from = jalali_to_gregorian(date_from)
        query = query.where(TruckLoad.date_gregorian >= greg_from)
        count_query = count_query.where(TruckLoad.date_gregorian >= greg_from)
    if date_to:
        greg_to = jalali_to_gregorian(date_to)
        query = query.where(TruckLoad.date_gregorian <= greg_to)
        count_query = count_query.where(TruckLoad.date_gregorian <= greg_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(TruckLoad.id).offset((page - 1) * size).limit(size)
    )
    trucks = result.scalars().all()
    return trucks, total


async def get_truck_with_attachments(db: AsyncSession, truck_id: int):
    truck = await get_truck_or_404(db, truck_id)
    attachments_result = await db.execute(
        select(Attachment).where(
            Attachment.entity_type == EntityType.TRUCK.value,
            Attachment.entity_id == truck_id,
        )
    )
    attachments = attachments_result.scalars().all()
    return truck, list(attachments)


async def create_truck(db: AsyncSession, data: TruckLoadCreate) -> TruckLoad:
    greg_date = jalali_to_gregorian(data.date_jalali)

    # Check duplicate receipt_number
    existing = await db.execute(
        select(TruckLoad).where(TruckLoad.receipt_number == data.receipt_number)
    )
    if existing.scalar_one_or_none():
        raise ConflictException(
            f"TruckLoad with receipt_number {data.receipt_number} already exists"
        )

    # Determine status
    if data.status is not None:
        status_val = data.status.value
    else:
        status_val = RecordStatus.REGISTERED.value

    dump = data.model_dump(exclude={"status", "date_jalali"})
    truck = TruckLoad(
        **dump,
        date_jalali=data.date_jalali,
        date_gregorian=greg_date,
        status=status_val,
    )
    db.add(truck)
    await db.commit()
    await db.refresh(truck)
    return truck


async def update_truck(db: AsyncSession, truck_id: int, data: TruckLoadUpdate) -> TruckLoad:
    truck = await get_truck_or_404(db, truck_id)
    update_data = data.model_dump(exclude_unset=True)

    if "date_jalali" in update_data:
        truck.date_gregorian = jalali_to_gregorian(update_data["date_jalali"])

    if "receipt_number" in update_data and update_data["receipt_number"] != truck.receipt_number:
        existing = await db.execute(
            select(TruckLoad).where(
                TruckLoad.receipt_number == update_data["receipt_number"],
                TruckLoad.id != truck_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException(
                f"TruckLoad with receipt_number {update_data['receipt_number']} already exists"
            )

    # Auto-transition: if cost fields are added to a "registered" record → "costed"
    adding_cost = (
        "cost_per_ton_rials" in update_data or "total_cost_rials" in update_data
    )
    if adding_cost and truck.status == RecordStatus.REGISTERED.value:
        truck.status = RecordStatus.COSTED.value

    if "destination" in update_data:
        dest = update_data["destination"]
        update_data["destination"] = dest.value if hasattr(dest, "value") else dest

    for key, value in update_data.items():
        setattr(truck, key, value)

    await db.commit()
    await db.refresh(truck)
    return truck


async def delete_truck(db: AsyncSession, truck_id: int) -> None:
    truck = await get_truck_or_404(db, truck_id)
    if truck.status != RecordStatus.REGISTERED.value:
        raise ConflictException(
            f"Cannot delete TruckLoad with status '{truck.status}'. Only 'registered' records can be deleted."
        )
    await db.delete(truck)
    await db.commit()


async def patch_truck_status(
    db: AsyncSession, truck_id: int, data: TruckStatusPatch
) -> TruckLoad:
    truck = await get_truck_or_404(db, truck_id)

    current_order = STATUS_ORDER.get(RecordStatus(truck.status), -1)
    new_order = STATUS_ORDER.get(data.status, -1)

    # Validate no skipping and no going backward
    if new_order != current_order + 1:
        raise BadRequestException(
            f"Invalid status transition from '{truck.status}' to '{data.status.value}'. "
            f"Allowed transitions: registered→costed→paid"
        )

    # Validate that cost fields exist when transitioning to "costed"
    if data.status == RecordStatus.COSTED:
        if truck.cost_per_ton_rials is None and truck.total_cost_rials is None:
            raise BadRequestException(
                "Cannot transition to 'costed' without cost_per_ton_rials or total_cost_rials"
            )

    truck.status = data.status.value
    await db.commit()
    await db.refresh(truck)
    return truck
