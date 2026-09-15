from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.v1.authentication import router as authentication_router
from api.v1.categories import router as categories_router
from api.v1.attachments import router as attachments_router
from api.v1.chats import router as chats_router
from api.v1.incidents import router as incidents_router
from api.v1.investigation_notes import router as investigation_notes_router
from api.v1.users import router as users_router
from api.v1.audit import router as audit_router

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(authentication_router)
app.include_router(categories_router)
app.include_router(attachments_router)
app.include_router(chats_router)
app.include_router(incidents_router)
app.include_router(investigation_notes_router)
app.include_router(users_router)
app.include_router(audit_router)