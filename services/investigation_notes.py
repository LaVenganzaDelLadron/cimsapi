import mysql.connector
from fastapi import HTTPException

from core.database.migration import get_database
from request.investigation_notes_request import InvestigationRequest


def index(current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		if current_user["role"] == "admin":
			cursor.execute("SELECT * FROM investigation_notes ORDER BY id DESC")
		else:
			cursor.execute("SELECT n.* FROM investigation_notes n JOIN incidents i ON i.id = n.incident_id WHERE i.assigned_to = %s ORDER BY n.id DESC", (current_user["id"],))
		return cursor.fetchall()
	finally:
		cursor.close()
		database.close()


def store(request: InvestigationRequest, current_user):
	if current_user["role"] not in {"admin", "analyst"}:
		raise HTTPException(status_code=403, detail="Only admins and analysts can add investigation notes")
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute(
			"INSERT INTO investigation_notes (incident_id, analyst_id, note, recommendation) VALUES (%s, %s, %s, %s)",
			(request.incident_id, current_user["id"], request.note, request.recommendation),
		)
		database.commit()
		cursor.execute("SELECT * FROM investigation_notes WHERE id = %s", (cursor.lastrowid,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def show(note_id: int, current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT * FROM investigation_notes WHERE id = %s", (note_id,))
		note = cursor.fetchone()
		if note is None:
			raise HTTPException(status_code=404, detail="Investigation note not found")
		cursor.execute("SELECT assigned_to FROM incidents WHERE id = %s", (note["incident_id"],))
		incident = cursor.fetchone()
		if current_user["role"] != "admin" and incident["assigned_to"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="You cannot access this investigation note")
		return note
	finally:
		cursor.close()
		database.close()


def update(note_id: int, request: InvestigationRequest, current_user):
	if current_user["role"] not in {"admin", "analyst"}:
		raise HTTPException(status_code=403, detail="Only admins and analysts can update investigation notes")
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT id FROM investigation_notes WHERE id = %s", (note_id,))
		if cursor.fetchone() is None:
			raise HTTPException(status_code=404, detail="Investigation note not found")
		cursor.execute(
			"UPDATE investigation_notes SET incident_id = %s, analyst_id = %s, note = %s, recommendation = %s WHERE id = %s",
			(request.incident_id, current_user["id"], request.note, request.recommendation, note_id),
		)
		database.commit()
		cursor.execute("SELECT * FROM investigation_notes WHERE id = %s", (note_id,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def destroy(note_id: int, current_user):
	if current_user["role"] != "admin":
		raise HTTPException(status_code=403, detail="Only admins can delete investigation notes")
	database = get_database()
	cursor = database.cursor()
	try:
		cursor.execute("DELETE FROM investigation_notes WHERE id = %s", (note_id,))
		if cursor.rowcount == 0:
			database.rollback()
			raise HTTPException(status_code=404, detail="Investigation note not found")
		database.commit()
		return {"message": "Investigation note deleted successfully"}
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()
