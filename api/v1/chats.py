from fastapi import APIRouter, Depends

from core.security import get_current_user
from request.chat_request import ChatRequest
from services.chats import destroy, index, show, store, update

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("")
def list_chats(current_user=Depends(get_current_user)):
    return index(current_user)


@router.post("", status_code=201)
def create_chat(request: ChatRequest, current_user=Depends(get_current_user)):
    return store(request, current_user)


@router.get("/{chat_id}")
def get_chat(chat_id: int, current_user=Depends(get_current_user)):
    return show(chat_id, current_user)


@router.put("/{chat_id}")
def update_chat(chat_id: int, request: ChatRequest, current_user=Depends(get_current_user)):
    return update(chat_id, request, current_user)


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, current_user=Depends(get_current_user)):
    return destroy(chat_id, current_user)
