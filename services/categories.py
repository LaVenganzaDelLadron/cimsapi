import mysql.connector
from fastapi import HTTPException

from core.database.migration import get_database
from request.categories_request import CategoryRequest


def index(current_user):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM categories ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        cursor.close()
        database.close()

def store(request: CategoryRequest, current_user):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create categories")
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)",
            (request.name, request.description),
        )
        database.commit()
        cursor.execute("SELECT * FROM categories WHERE id = %s", (cursor.lastrowid,))
        return cursor.fetchone()
    except mysql.connector.Error as error:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()

def show(category_id: int, current_user):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    finally:
        cursor.close()
        database.close()

def update(category_id: int, request: CategoryRequest, current_user):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update categories")
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM categories WHERE id = %s", (category_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Category not found")
        cursor.execute(
            "UPDATE categories SET name = %s, description = %s WHERE id = %s",
            (request.name, request.description, category_id),
        )
        database.commit()
        cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        return cursor.fetchone()
    except mysql.connector.Error as error:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()

def destroy(category_id: int, current_user):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete categories")
    database = get_database()
    cursor = database.cursor()
    try:
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        if cursor.rowcount == 0:
            database.rollback()
            raise HTTPException(status_code=404, detail="Category not found")
        database.commit()
        return {"message": "Category deleted successfully"}
    except mysql.connector.Error as error:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()

