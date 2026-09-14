from fastapi import APIRouter, Depends

from core.security import require_roles
from services.audit import index

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("")
def list_audit_logs(current_user=Depends(require_roles("admin"))):
    return index()
