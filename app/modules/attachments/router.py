from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.attachments import service
from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import EntityType

router = APIRouter()


@router.post("/upload", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    entity_type: EntityType = Form(...),
    entity_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    return await service.upload_attachment(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        filename=file.filename or "upload",
        content=content,
    )


@router.get("/by-entity/", response_model=List[AttachmentResponse])
async def list_by_entity(
    entity_type: EntityType,
    entity_id: int,
    db: AsyncSession = Depends(get_db),
):
    attachments = await service.list_attachments_by_entity(
        db, entity_type.value, entity_id
    )
    return [AttachmentResponse.model_validate(a) for a in attachments]


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_attachment_or_404(db, attachment_id)


@router.get("/{attachment_id}/download")
async def download_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    attachment = await service.get_attachment_or_404(db, attachment_id)
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.file_name,
        media_type="application/octet-stream",
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_attachment(db, attachment_id)
