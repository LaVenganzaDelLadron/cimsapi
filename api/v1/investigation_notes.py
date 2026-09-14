from fastapi import APIRouter, Depends

from core.security import get_current_user
from request.investigation_notes_request import InvestigationRequest
from services.investigation_notes import destroy, index, show, store, update

router = APIRouter(prefix="/investigation-notes", tags=["Investigation Notes"])


@router.get("")
def list_investigation_notes(current_user=Depends(get_current_user)):
    return index(current_user)


@router.post("", status_code=201)
def create_investigation_note(request: InvestigationRequest, current_user=Depends(get_current_user)):
    return store(request, current_user)


@router.get("/{note_id}")
def get_investigation_note(note_id: int, current_user=Depends(get_current_user)):
    return show(note_id, current_user)


@router.put("/{note_id}")
def update_investigation_note(note_id: int, request: InvestigationRequest, current_user=Depends(get_current_user)):
    return update(note_id, request, current_user)


@router.delete("/{note_id}")
def delete_investigation_note(note_id: int, current_user=Depends(get_current_user)):
    return destroy(note_id, current_user)
