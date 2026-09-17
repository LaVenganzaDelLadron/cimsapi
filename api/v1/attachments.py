from fastapi import APIRouter, Depends, File, Form, UploadFile

from core.security import get_current_user
from request.attachment_request import AttachmentRequest
from services.attachments import destroy, index, show, store, update

router = APIRouter(prefix="/attachments", tags=["Attachments"])


@router.get("")
def list_attachments(current_user=Depends(get_current_user)):
    return index(current_user)


@router.post("", status_code=201)
async def create_attachment(
    incident_id: int = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    return await store(incident_id, file, current_user)


@router.get("/{attachment_id}")
def get_attachment(attachment_id: int, current_user=Depends(get_current_user)):
    return show(attachment_id, current_user)


@router.put("/{attachment_id}")
def update_attachment(attachment_id: int, request: AttachmentRequest, current_user=Depends(get_current_user)):
    return update(attachment_id, request, current_user)


@router.delete("/{attachment_id}")
def delete_attachment(attachment_id: int, current_user=Depends(get_current_user)):
    return destroy(attachment_id, current_user)
