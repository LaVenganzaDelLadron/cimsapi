from fastapi import APIRouter, Depends
from core.security import get_current_user

from request.incident_request import IncidentRequest
from services.incidents import destroy, index, show, store, update

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("")
def list_incidents(current_user=Depends(get_current_user)):
    return index(current_user)


@router.post("", status_code=201)
def create_incident(request: IncidentRequest, current_user=Depends(get_current_user)):
    return store(request, current_user)


@router.get("/{incident_id}")
def get_incident(incident_id: int, current_user=Depends(get_current_user)):
    return show(incident_id, current_user)


@router.put("/{incident_id}")
def update_incident(incident_id: int, request: IncidentRequest, current_user=Depends(get_current_user)):
    return update(incident_id, request, current_user)


@router.delete("/{incident_id}")
def delete_incident(incident_id: int, current_user=Depends(get_current_user)):
    return destroy(incident_id, current_user)
