import mysql.connector
from fastapi import HTTPException

from core.database.migration import get_database
from request.attachment_request import AttachmentRequest


def index(current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		if current_user["role"] == "admin":
			cursor.execute("SELECT * FROM attachments ORDER BY id DESC")
		else:
			cursor.execute("SELECT a.* FROM attachments a JOIN incidents i ON i.id = a.incident_id WHERE i.user_id = %s OR i.assigned_to = %s ORDER BY a.id DESC", (current_user["id"], current_user["id"]))
		return cursor.fetchall()
	finally:
		cursor.close()
		database.close()


def store(request: AttachmentRequest, current_user):
	if current_user["role"] not in {"admin", "analyst"}:
		raise HTTPException(status_code=403, detail="Only admins and analysts can upload attachments")
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute(
			"INSERT INTO attachments (incident_id, filename, filepath, filetype, uploaded_by) VALUES (%s, %s, %s, %s, %s)",
			(request.incident_id, request.filename, request.filepath, request.filetype, current_user["id"]),
		)
		database.commit()
		cursor.execute("SELECT * FROM attachments WHERE id = %s", (cursor.lastrowid,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def show(attachment_id: int, current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT * FROM attachments WHERE id = %s", (attachment_id,))
		attachment = cursor.fetchone()
		if attachment is None:
			raise HTTPException(status_code=404, detail="Attachment not found")
		cursor.execute("SELECT user_id, assigned_to FROM incidents WHERE id = %s", (attachment["incident_id"],))
		incident = cursor.fetchone()
		if current_user["role"] != "admin" and current_user["id"] not in {incident["user_id"], incident["assigned_to"]}:
			raise HTTPException(status_code=403, detail="You cannot access this attachment")
		return attachment
	finally:
		cursor.close()
		database.close()


def update(attachment_id: int, request: AttachmentRequest, current_user):
	if current_user["role"] not in {"admin", "analyst"}:
		raise HTTPException(status_code=403, detail="Only admins and analysts can update attachments")
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT id FROM attachments WHERE id = %s", (attachment_id,))
		if cursor.fetchone() is None:
			raise HTTPException(status_code=404, detail="Attachment not found")
		cursor.execute(
			"UPDATE attachments SET incident_id = %s, filename = %s, filepath = %s, filetype = %s, uploaded_by = %s WHERE id = %s",
			(request.incident_id, request.filename, request.filepath, request.filetype, current_user["id"], attachment_id),
		)
		database.commit()
		cursor.execute("SELECT * FROM attachments WHERE id = %s", (attachment_id,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def destroy(attachment_id: int, current_user):
	if current_user["role"] != "admin":
		raise HTTPException(status_code=403, detail="Only admins can delete attachments")
	database = get_database()
	cursor = database.cursor()
	try:
		cursor.execute("DELETE FROM attachments WHERE id = %s", (attachment_id,))
		if cursor.rowcount == 0:
			database.rollback()
			raise HTTPException(status_code=404, detail="Attachment not found")
		database.commit()
		return {"message": "Attachment deleted successfully"}
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()
