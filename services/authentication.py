import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException

from core.database.migration import get_database
from request.signin_request import SigninRequest
from request.signup_request import SignupRequest



JWT_SECRET = "lol"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )
    return password_hash.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )

def create_access_token(user_id: int, email: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expires_at,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def signup(request: SignupRequest):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (request.email,)
        )
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="Email already registered"
                )
        

        hashed_password = hash_password(request.password)

        cursor.execute(
            "INSERT INTO users (email, firstname, lastname, password, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (request.email, request.firstname, request.lastname, hashed_password, "user", "active")
        )
        database.commit()
        user_id = cursor.lastrowid

        return {
            "id": user_id,
            "email": request.email,
            "firstname": request.firstname,
            "lastname": request.lastname,
            "role": "user",
            "status": "active"
        }

    except HTTPException:
        database.rollback()
        raise
    except Exception as error:
        database.rollback()
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()


def signin(request: SigninRequest):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, email, firstname, lastname, password, role, status
            FROM users
            WHERE email = %s
            """,
            (request.email,),
        )

        user = cursor.fetchone()

        if not user or not verify_password(
            request.password,
            user["password"],
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        if user["status"] != "active":
            raise HTTPException(
                status_code=403,
                detail="Account is not active",
            )

        token = create_access_token(user["id"], user["email"], user["role"])

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "firstname": user["firstname"],
                "lastname": user["lastname"],
                "role": user["role"],
                "status": user["status"],
            },
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
        database.close()
