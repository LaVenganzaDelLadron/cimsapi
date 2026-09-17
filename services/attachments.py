import re
from pathlib import Path
from uuid import uuid4

import mysql.connector
from fastapi import HTTPException, UploadFile

from core.database.migration import get_database
from core.config import get_settings
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


def _safe_filename(filename: str) -> str:
	return re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name) or "attachment"


def _storage_path(filepath: str) -> Path | None:
	root = Path(get_settings().attachment_storage_dir).resolve()
	path = Path(filepath)
	if not path.is_absolute():
		path = Path.cwd() / path
	try:
		path.resolve().relative_to(root)
	except ValueError:
		return None
	return path.resolve()


async def store(incident_id: int, file: UploadFile, current_user):
	if current_user["role"] not in {"admin", "analyst"}:
		raise HTTPException(status_code=403, detail="Only admins and analysts can upload attachments")
	settings = get_settings()
	original_filename = _safe_filename(file.filename or "attachment")
	storage_dir = Path(settings.attachment_storage_dir)
	storage_dir.mkdir(parents=True, exist_ok=True)
	stored_path = storage_dir / f"{uuid4().hex}_{original_filename}"
	file_size = 0
	try:
		with stored_path.open("wb") as destination:
			while chunk := await file.read(1024 * 1024):
				file_size += len(chunk)
				if file_size > settings.attachment_max_size:
					raise HTTPException(status_code=413, detail="Attachment exceeds the maximum allowed size")
				destination.write(chunk)
	except HTTPException:
		stored_path.unlink(missing_ok=True)
		raise
	finally:
		await file.close()

	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute(
			"INSERT INTO attachments (incident_id, filename, filepath, filetype, uploaded_by) VALUES (%s, %s, %s, %s, %s)",
			(incident_id, original_filename, str(stored_path), file.content_type or "application/octet-stream", current_user["id"]),
		)
		database.commit()
		cursor.execute("SELECT * FROM attachments WHERE id = %s", (cursor.lastrowid,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		stored_path.unlink(missing_ok=True)
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
		cursor.execute("SELECT filepath FROM attachments WHERE id = %s", (attachment_id,))
		attachment = cursor.fetchone()
		if attachment is None:
			raise HTTPException(status_code=404, detail="Attachment not found")
		cursor.execute("DELETE FROM attachments WHERE id = %s", (attachment_id,))
		if cursor.rowcount == 0:
			database.rollback()
			raise HTTPException(status_code=404, detail="Attachment not found")
		database.commit()
		if path := _storage_path(attachment[0]):
			path.unlink(missing_ok=True)
		return {"message": "Attachment deleted successfully"}
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()
