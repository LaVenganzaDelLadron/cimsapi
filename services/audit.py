import json

from core.database.migration import get_database


def record(actor_id, action: str, resource_type: str, resource_id=None, details=None):
    database = get_database()
    cursor = database.cursor()
    try:
        cursor.execute(
            "INSERT INTO audit_logs (actor_id, action, resource_type, resource_id, details) VALUES (%s, %s, %s, %s, %s)",
            (actor_id, action, resource_type, resource_id, json.dumps(details) if details else None),
        )
        database.commit()
    finally:
        cursor.close()
        database.close()


def index():
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        cursor.close()
        database.close()
