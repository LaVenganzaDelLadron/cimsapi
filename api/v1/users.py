from fastapi import APIRouter, Depends

from core.security import require_roles
from request.user_request import UserRequest
from services.users import index, show, store, update

router = APIRouter(prefix="/users", tags=["Users"])
admin_only = require_roles("admin")


@router.get("")
def list_users(current_user=Depends(admin_only)):
    return index()


@router.post("", status_code=201)
def create_user(request: UserRequest, current_user=Depends(admin_only)):
    return store(request, current_user)


@router.get("/{user_id}")
def get_user(user_id: int, current_user=Depends(admin_only)):
    return show(user_id)


@router.put("/{user_id}")
def update_user(user_id: int, request: UserRequest, current_user=Depends(admin_only)):
    return update(user_id, request, current_user)
