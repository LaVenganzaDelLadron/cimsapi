import mysql.connector
from fastapi import HTTPException

from core.database.migration import get_database
from core.ai.pipeline import AIPipeline
from request.chat_request import ChatRequest

_pipeline = None


def _get_pipeline():
	global _pipeline
	if _pipeline is None:
		_pipeline = AIPipeline()
	return _pipeline


def _generate_response(message: str, user_id: int) -> str:
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute(
			"SELECT userinput, response FROM chats WHERE user_id = %s ORDER BY id DESC LIMIT 20",
			(user_id,),
		)
		history_rows = list(reversed(cursor.fetchall()))
	finally:
		cursor.close()
		database.close()

	history = []
	for row in history_rows:
		history.extend([
			{"role": "user", "content": row["userinput"]},
			{"role": "assistant", "content": row["response"]},
		])
	try:
		return _get_pipeline().respond(message, history)
	except Exception as error:
		raise HTTPException(status_code=502, detail="AI service is temporarily unavailable") from error


def index(current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		if current_user["role"] == "admin":
			cursor.execute("SELECT * FROM chats ORDER BY id DESC")
		else:
			cursor.execute("SELECT * FROM chats WHERE user_id = %s ORDER BY id DESC", (current_user["id"],))
		return cursor.fetchall()
	finally:
		cursor.close()
		database.close()


def store(request: ChatRequest, current_user):
	answer = _generate_response(request.message, current_user["id"])
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute(
			"INSERT INTO chats (user_id, userinput, response) VALUES (%s, %s, %s)",
			(current_user["id"], request.message, answer),
		)
		database.commit()
		cursor.execute("SELECT * FROM chats WHERE id = %s", (cursor.lastrowid,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def show(chat_id: int, current_user):
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
		chat = cursor.fetchone()
		if chat is None:
			raise HTTPException(status_code=404, detail="Chat not found")
		if current_user["role"] != "admin" and chat["user_id"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="You can only access your own chats")
		return chat
	finally:
		cursor.close()
		database.close()


def update(chat_id: int, request: ChatRequest, current_user):
	answer = _generate_response(request.message, current_user["id"])
	database = get_database()
	cursor = database.cursor(dictionary=True)
	try:
		cursor.execute("SELECT id FROM chats WHERE id = %s", (chat_id,))
		if cursor.fetchone() is None:
			raise HTTPException(status_code=404, detail="Chat not found")
		cursor.execute("SELECT user_id FROM chats WHERE id = %s", (chat_id,))
		chat = cursor.fetchone()
		if current_user["role"] != "admin" and chat["user_id"] != current_user["id"]:
			raise HTTPException(status_code=403, detail="You can only edit your own chats")
		cursor.execute(
			"UPDATE chats SET user_id = %s, userinput = %s, response = %s WHERE id = %s",
			(chat["user_id"], request.message, answer, chat_id),
		)
		database.commit()
		cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
		return cursor.fetchone()
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()


def destroy(chat_id: int, current_user):
	if current_user["role"] != "admin":
		raise HTTPException(status_code=403, detail="Only admins can delete chats")
	database = get_database()
	cursor = database.cursor()
	try:
		cursor.execute("DELETE FROM chats WHERE id = %s", (chat_id,))
		if cursor.rowcount == 0:
			database.rollback()
			raise HTTPException(status_code=404, detail="Chat not found")
		database.commit()
		return {"message": "Chat deleted successfully"}
	except mysql.connector.Error as error:
		database.rollback()
		raise HTTPException(status_code=500, detail=str(error))
	finally:
		cursor.close()
		database.close()
