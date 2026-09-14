from fastapi import APIRouter, Depends

from core.security import get_current_user, require_roles
from request.categories_request import CategoryRequest
from services.categories import destroy, index, show, store, update

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
def list_categories(current_user=Depends(get_current_user)):
    return index(current_user)


@router.post("", status_code=201)
def create_category(request: CategoryRequest, current_user=Depends(require_roles("admin"))):
    return store(request, current_user)


@router.get("/{category_id}")
def get_category(category_id: int, current_user=Depends(get_current_user)):
    return show(category_id, current_user)


@router.put("/{category_id}")
def update_category(category_id: int, request: CategoryRequest, current_user=Depends(require_roles("admin"))):
    return update(category_id, request, current_user)


@router.delete("/{category_id}")
def delete_category(category_id: int, current_user=Depends(require_roles("admin"))):
    return destroy(category_id, current_user)