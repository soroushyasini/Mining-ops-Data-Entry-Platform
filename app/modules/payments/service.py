from datetime import time as time_type
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment, PaymentGroup
from app.modules.payments.schemas import PaymentGroupCreate, PaymentGroupUpdate, PaymentItemCreate
from app.modules.attachments.models import Attachment
from app.shared.enums import EntityType, RecordStatus
from app.shared.exceptions import BadRequestException, ConflictException, NotFoundException
from app.shared.jalali import jalali_to_gregorian


# ---------------------------------------------------------------------------
# Entity helpers
# ---------------------------------------------------------------------------

async def _get_entity_or_raise(db: AsyncSession, entity_type: EntityType, entity_id: int):
    """Return the entity model instance or raise NotFoundException."""
    from app.modules.trucks.models import TruckLoad
    from app.modules.bunkers.models import BunkerLoad
    from app.modules.grinding.models import GrindingLedgerEntry
    from app.modules.lab.models import LabIssueBatch

    model_map = {
        EntityType.TRUCK: TruckLoad,
        EntityType.BUNKER: BunkerLoad,
        EntityType.GRINDING: GrindingLedgerEntry,
        EntityType.LAB_BATCH: LabIssueBatch,
    }
    model = model_map.get(entity_type)
    if model is None:
        raise BadRequestException(f"Unsupported entity_type: {entity_type.value}")

    result = await db.execute(select(model).where(model.id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise NotFoundException(
            f"{entity_type.value} with id {entity_id} not found"
        )
    return entity


async def _update_entity_status(
    db: AsyncSession, entity_type: EntityType, entity_id: int, new_status: str
) -> None:
    """Update the status of the referenced entity."""
    entity = await _get_entity_or_raise(db, entity_type, entity_id)
    entity.status = new_status


def _parse_time(time_str: Optional[str]) -> Optional[time_type]:
    """Parse 'HH:MM' string to time object."""
    if time_str is None:
        return None
    parts = time_str.split(":")
    if len(parts) != 2:
        raise BadRequestException(f"Invalid payment_time format '{time_str}'. Expected HH:MM")
    try:
        return time_type(int(parts[0]), int(parts[1]))
    except (ValueError, TypeError) as exc:
        raise BadRequestException(f"Invalid payment_time '{time_str}': {exc}") from exc


def _revert_status(entity_type: EntityType) -> str:
    """Return the status to revert to when a payment is deleted."""
    if entity_type == EntityType.LAB_BATCH:
        return RecordStatus.INVOICED.value
    return RecordStatus.COSTED.value


# ---------------------------------------------------------------------------
# PaymentGroup CRUD
# ---------------------------------------------------------------------------

async def get_group_or_404(db: AsyncSession, group_id: int) -> PaymentGroup:
    result = await db.execute(
        select(PaymentGroup).where(PaymentGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise NotFoundException(f"PaymentGroup with id {group_id} not found")
    return group


async def list_payment_groups(
    db: AsyncSession,
    page: int,
    size: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    payer_name: Optional[str] = None,
    bank_name: Optional[str] = None,
):
    query = select(PaymentGroup)
    count_query = select(func.count(PaymentGroup.id))

    if date_from:
        greg_from = jalali_to_gregorian(date_from)
        query = query.where(PaymentGroup.payment_date_gregorian >= greg_from)
        count_query = count_query.where(PaymentGroup.payment_date_gregorian >= greg_from)
    if date_to:
        greg_to = jalali_to_gregorian(date_to)
        query = query.where(PaymentGroup.payment_date_gregorian <= greg_to)
        count_query = count_query.where(PaymentGroup.payment_date_gregorian <= greg_to)
    if payer_name:
        query = query.where(PaymentGroup.payer_name.ilike(f"%{payer_name}%"))
        count_query = count_query.where(PaymentGroup.payer_name.ilike(f"%{payer_name}%"))
    if bank_name:
        query = query.where(PaymentGroup.bank_name.ilike(f"%{bank_name}%"))
        count_query = count_query.where(PaymentGroup.bank_name.ilike(f"%{bank_name}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(PaymentGroup.id).offset((page - 1) * size).limit(size)
    )
    groups = result.scalars().all()
    return groups, total


async def get_group_with_details(db: AsyncSession, group_id: int):
    group = await get_group_or_404(db, group_id)

    payments_result = await db.execute(
        select(Payment).where(Payment.group_id == group_id)
    )
    payments = payments_result.scalars().all()

    attachments_result = await db.execute(
        select(Attachment).where(
            Attachment.entity_type == EntityType.PAYMENT_GROUP.value,
            Attachment.entity_id == group_id,
        )
    )
    attachments = attachments_result.scalars().all()
    return group, list(payments), list(attachments)


async def create_payment_group(
    db: AsyncSession, data: PaymentGroupCreate
) -> PaymentGroup:
    # Validate all entities exist and are in valid status
    for item in data.payments:
        entity = await _get_entity_or_raise(db, item.entity_type, item.entity_id)
        entity_status = entity.status
        valid_statuses = {RecordStatus.COSTED.value, RecordStatus.INVOICED.value}
        if entity_status not in valid_statuses:
            if entity_status == RecordStatus.PAID.value:
                raise ConflictException(
                    f"{item.entity_type.value} with id {item.entity_id} is already 'paid'"
                )
            raise BadRequestException(
                f"{item.entity_type.value} with id {item.entity_id} has status '{entity_status}'. "
                "Only 'costed' or 'invoiced' entities can be paid."
            )

    greg_date = jalali_to_gregorian(data.payment_date_jalali)
    payment_time = _parse_time(data.payment_time)

    group = PaymentGroup(
        payment_date_jalali=data.payment_date_jalali,
        payment_date_gregorian=greg_date,
        payment_time=payment_time,
        payer_name=data.payer_name,
        bank_name=data.bank_name,
        bank_account_number=data.bank_account_number,
        total_amount_rials=data.total_amount_rials,
        note=data.note,
    )
    db.add(group)
    await db.flush()  # get group.id

    for item in data.payments:
        payment = Payment(
            group_id=group.id,
            entity_type=item.entity_type.value,
            entity_id=item.entity_id,
            amount_rials=item.amount_rials,
        )
        db.add(payment)
        await _update_entity_status(db, item.entity_type, item.entity_id, RecordStatus.PAID.value)

    await db.commit()
    await db.refresh(group)
    return group


async def update_payment_group(
    db: AsyncSession, group_id: int, data: PaymentGroupUpdate
) -> PaymentGroup:
    group = await get_group_or_404(db, group_id)
    update_data = data.model_dump(exclude_unset=True)

    if "payment_date_jalali" in update_data:
        group.payment_date_gregorian = jalali_to_gregorian(update_data["payment_date_jalali"])

    if "payment_time" in update_data:
        update_data["payment_time"] = _parse_time(update_data["payment_time"])

    for key, value in update_data.items():
        setattr(group, key, value)

    await db.commit()
    await db.refresh(group)
    return group


async def delete_payment_group(db: AsyncSession, group_id: int) -> None:
    group = await get_group_or_404(db, group_id)

    payments_result = await db.execute(
        select(Payment).where(Payment.group_id == group_id)
    )
    payments = payments_result.scalars().all()

    for payment in payments:
        entity_type = EntityType(payment.entity_type)
        revert_status = _revert_status(entity_type)
        await _update_entity_status(db, entity_type, payment.entity_id, revert_status)
        await db.delete(payment)

    await db.delete(group)
    await db.commit()


# ---------------------------------------------------------------------------
# Individual Payment items
# ---------------------------------------------------------------------------

async def get_payment_or_404(db: AsyncSession, payment_id: int) -> Payment:
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise NotFoundException(f"Payment with id {payment_id} not found")
    return payment


async def list_payment_items(
    db: AsyncSession,
    page: int,
    size: int,
    group_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
):
    query = select(Payment)
    count_query = select(func.count(Payment.id))

    if group_id is not None:
        query = query.where(Payment.group_id == group_id)
        count_query = count_query.where(Payment.group_id == group_id)
    if entity_type:
        query = query.where(Payment.entity_type == entity_type)
        count_query = count_query.where(Payment.entity_type == entity_type)
    if entity_id is not None:
        query = query.where(Payment.entity_id == entity_id)
        count_query = count_query.where(Payment.entity_id == entity_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(
        query.order_by(Payment.id).offset((page - 1) * size).limit(size)
    )
    items = result.scalars().all()
    return items, total


async def delete_payment_item(db: AsyncSession, payment_id: int) -> None:
    payment = await get_payment_or_404(db, payment_id)
    entity_type = EntityType(payment.entity_type)
    revert_status = _revert_status(entity_type)
    await _update_entity_status(db, entity_type, payment.entity_id, revert_status)
    await db.delete(payment)
    await db.commit()
