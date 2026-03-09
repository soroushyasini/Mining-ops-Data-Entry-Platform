from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.payments import service
from app.modules.payments.schemas import (
    PaymentGroupCreate,
    PaymentGroupResponse,
    PaymentGroupUpdate,
    PaymentItemResponse,
)
from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import EntityType
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


def _serialize_group(group, payments=None, attachments=None) -> PaymentGroupResponse:
    """Build a PaymentGroupResponse, converting payment_time to string."""
    payment_time_str = None
    if group.payment_time is not None:
        payment_time_str = group.payment_time.strftime("%H:%M")

    response = PaymentGroupResponse(
        id=group.id,
        payment_date_jalali=group.payment_date_jalali,
        payment_date_gregorian=group.payment_date_gregorian,
        payment_time=payment_time_str,
        payer_name=group.payer_name,
        bank_name=group.bank_name,
        bank_account_number=group.bank_account_number,
        total_amount_rials=group.total_amount_rials,
        note=group.note,
        created_at=group.created_at,
        payments=[PaymentItemResponse.model_validate(p) for p in (payments or [])],
        payments_count=len(payments) if payments is not None else 0,
        attachments=[AttachmentResponse.model_validate(a) for a in (attachments or [])],
    )
    return response


# ---------------------------------------------------------------------------
# Payment Groups
# ---------------------------------------------------------------------------

@router.get("/groups/", response_model=PaginatedResponse[PaymentGroupResponse])
async def list_payment_groups(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    payer_name: Optional[str] = None,
    bank_name: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    groups, total = await service.list_payment_groups(
        db,
        pagination.page,
        pagination.size,
        date_from=date_from,
        date_to=date_to,
        payer_name=payer_name,
        bank_name=bank_name,
    )
    return PaginatedResponse.create(
        items=[_serialize_group(g) for g in groups],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/groups/{group_id}", response_model=PaymentGroupResponse)
async def get_payment_group(group_id: int, db: AsyncSession = Depends(get_db)):
    group, payments, attachments = await service.get_group_with_details(db, group_id)
    return _serialize_group(group, payments, attachments)


@router.post("/groups/", response_model=PaymentGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_group(data: PaymentGroupCreate, db: AsyncSession = Depends(get_db)):
    group = await service.create_payment_group(db, data)
    # Re-fetch payments
    _, payments, attachments = await service.get_group_with_details(db, group.id)
    return _serialize_group(group, payments, attachments)


@router.put("/groups/{group_id}", response_model=PaymentGroupResponse)
async def update_payment_group(
    group_id: int, data: PaymentGroupUpdate, db: AsyncSession = Depends(get_db)
):
    group = await service.update_payment_group(db, group_id, data)
    _, payments, attachments = await service.get_group_with_details(db, group.id)
    return _serialize_group(group, payments, attachments)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_group(group_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_payment_group(db, group_id)


# ---------------------------------------------------------------------------
# Individual Payment Items
# ---------------------------------------------------------------------------

@router.get("/items/", response_model=PaginatedResponse[PaymentItemResponse])
async def list_payment_items(
    group_id: Optional[int] = None,
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[int] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    items, total = await service.list_payment_items(
        db,
        pagination.page,
        pagination.size,
        group_id=group_id,
        entity_type=entity_type.value if entity_type else None,
        entity_id=entity_id,
    )
    return PaginatedResponse.create(
        items=[PaymentItemResponse.model_validate(i) for i in items],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/items/{payment_id}", response_model=PaymentItemResponse)
async def get_payment_item(payment_id: int, db: AsyncSession = Depends(get_db)):
    payment = await service.get_payment_or_404(db, payment_id)
    return PaymentItemResponse.model_validate(payment)


@router.delete("/items/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_item(payment_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_payment_item(db, payment_id)
