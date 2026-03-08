import os

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.attachments.models import Attachment
from app.shared.enums import EntityType
from app.shared.exceptions import BadRequestException, NotFoundException

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def upload_attachment(
    db: AsyncSession,
    entity_type: EntityType,
    entity_id: int,
    filename: str,
    content: bytes,
) -> Attachment:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestException(
            f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    if len(content) > MAX_FILE_SIZE:
        raise BadRequestException("File size exceeds 10MB limit")

    # Build storage path
    dir_path = os.path.join(settings.upload_dir, entity_type.value, str(entity_id))
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    attachment = Attachment(
        entity_type=entity_type.value,
        entity_id=entity_id,
        file_name=filename,
        file_path=file_path,
        file_type=ext,
        file_size_bytes=len(content),
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment


async def get_attachment_or_404(db: AsyncSession, attachment_id: int) -> Attachment:
    result = await db.execute(
        select(Attachment).where(Attachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise NotFoundException(f"Attachment with id {attachment_id} not found")
    return attachment


async def list_attachments_by_entity(
    db: AsyncSession, entity_type: str, entity_id: int
):
    result = await db.execute(
        select(Attachment).where(
            Attachment.entity_type == entity_type,
            Attachment.entity_id == entity_id,
        )
    )
    return result.scalars().all()


async def delete_attachment(db: AsyncSession, attachment_id: int) -> None:
    attachment = await get_attachment_or_404(db, attachment_id)

    # Remove file from disk
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    await db.delete(attachment)
    await db.commit()
