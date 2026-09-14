import mysql.connector
from fastapi import HTTPException

from core.database.migration import get_database
from services.audit import record
from services.authentication import hash_password
from request.user_request import UserRequest


def index():
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, firstname, lastname, role, status, created_at, updated_at FROM users ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        cursor.close()
        database.close()


def show(user_id: int):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, firstname, lastname, role, status, created_at, updated_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        cursor.close()
        database.close()


def store(request: UserRequest, actor):
    if request.password is None:
        raise HTTPException(status_code=422, detail="Password is required when creating a user")
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (request.email,))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=409, detail="Email already registered")
        cursor.execute(
            "INSERT INTO users (email, firstname, lastname, password, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (request.email, request.firstname, request.lastname, hash_password(request.password), request.role, request.status),
        )
        database.commit()
        user_id = cursor.lastrowid
        record(actor["id"], "create", "user", user_id, {"role": request.role})
        return show(user_id)
    except HTTPException:
        database.rollback()
        raise
    except mysql.connector.Error as error:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()


def update(user_id: int, request: UserRequest, actor):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, role, status FROM users WHERE id = %s", (user_id,))
        existing = cursor.fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="User not found")
        if existing["role"] == "admin" and (request.role != "admin" or request.status != "active"):
            cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'admin' AND status = 'active'")
            if cursor.fetchone()["count"] <= 1:
                raise HTTPException(status_code=409, detail="The last active admin cannot be disabled or demoted")
        password_clause = ", password = %s" if request.password else ""
        values = [request.email, request.firstname, request.lastname, request.role, request.status]
        if request.password:
            values.append(hash_password(request.password))
        values.append(user_id)
        cursor.execute(
            f"UPDATE users SET email = %s, firstname = %s, lastname = %s, role = %s, status = %s{password_clause} WHERE id = %s",
            tuple(values),
        )
        database.commit()
        record(actor["id"], "update", "user", user_id, {"role": request.role, "status": request.status})
        return show(user_id)
    except HTTPException:
        database.rollback()
        raise
    except mysql.connector.Error as error:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()
