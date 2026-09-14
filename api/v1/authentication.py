from fastapi import APIRouter, HTTPException

from request.signin_request import SigninRequest
from request.signup_request import SignupRequest
from services.authentication import signup, signin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup")
async def register(request: SignupRequest):
    return signup(request)


@router.post("/signin")
async def signin(request: SigninRequest):
    return signin(request)