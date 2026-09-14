import mysql.connector
from fastapi import HTTPException

from core.database.migration import get_database
from request.incident_request import IncidentRequest
from services.audit import record


def index(current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		if current_user["role"] == "admin":
			cursor.execute("SELECT * FROM incidents ORDER BY id DESC")
		elif current_user["role"] == "analyst":
			cursor.execute("SELECT * FROM incidents WHERE assigned_to = %s ORDER BY id DESC", (current_user["id"],))
		else:
			cursor.execute("SELECT * FROM incidents WHERE user_id = %s ORDER BY id DESC", (current_user["id"],))
		return cursor.fetchall()
	finally:
		cursor.close()
		database.close()


def store(request: IncidentRequest, current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute(
			"INSERT INTO incidents (user_id, category_id, title, description, severity, status, location, incident_date, assigned_to, resolve_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
			(current_user["id"], request.category_id, request.title, request.description, request.severity, "new", request.location, request.incident_date, None, request.resolve_at),
		)
		database.commit()
		record(current_user["id"], "create", "incident", cursor.lastrowid)
		cursor.execute("SELECT * FROM incidents WHERE id = %s", (cursor.lastrowid,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def show(incident_id: int, current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
		incident = cursor.fetchone()
		if incident is None:
			raise HTTPException(status_code=404, detail="Incident not found")
		if current_user["role"] == "user" and incident["user_id"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="You can only access your own incidents")
		if current_user["role"] == "analyst" and incident["assigned_to"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="Incident is not assigned to you")
		return incident
	finally:
		cursor.close()
		database.close()


def update(incident_id: int, request: IncidentRequest, current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
		cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
		incident = cursor.fetchone()
		if incident is None:
			raise HTTPException(status_code=404, detail="Incident not found")
		if incident["status"] == "closed":
			raise HTTPException(status_code=409, detail="Closed incidents cannot be edited")
		if current_user["role"] == "user" and incident["user_id"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="You can only edit your own incidents")
		if current_user["role"] == "analyst" and incident["assigned_to"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="Incident is not assigned to you")
		if current_user["role"] == "user" and request.status not in {incident["status"], "new"}:
			raise HTTPException(status_code=403, detail="Users cannot change incident status")
		if current_user["role"] == "analyst" and request.status == "closed":
			raise HTTPException(status_code=403, detail="Only admins can close incidents")
		assigned_to = request.assigned_to if current_user["role"] == "admin" else incident["assigned_to"]
		status = request.status if current_user["role"] != "user" else incident["status"]
		if assigned_to is not None:
			cursor.execute("SELECT id FROM users WHERE id = %s AND role = 'analyst' AND status = 'active'", (assigned_to,))
			if cursor.fetchone() is None:
				raise HTTPException(status_code=422, detail="assigned_to must be an active analyst")
		cursor.execute(
			"UPDATE incidents SET user_id = %s, category_id = %s, title = %s, description = %s, severity = %s, status = %s, location = %s, incident_date = %s, assigned_to = %s, resolve_at = %s WHERE id = %s",
			(incident["user_id"], request.category_id, request.title, request.description, request.severity, status, request.location, request.incident_date, assigned_to, request.resolve_at, incident_id),
		)
		database.commit()
		record(current_user["id"], "update", "incident", incident_id, {"status": status, "assigned_to": assigned_to})
		cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def destroy(incident_id: int, current_user):
	if current_user["role"] != "admin":
		raise HTTPException(status_code=403, detail="Only admins can delete incidents")
	database = get_database()
	cursor = database.cursor()
	try:
		cursor.execute("DELETE FROM incidents WHERE id = %s", (incident_id,))
		if cursor.rowcount == 0:
			database.rollback()
			raise HTTPException(status_code=404, detail="Incident not found")
		database.commit()
		record(current_user["id"], "delete", "incident", incident_id)
		return {"message": "Incident deleted successfully"}
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()
