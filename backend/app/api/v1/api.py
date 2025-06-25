from fastapi import APIRouter

from app.api.v1 import auth, chat, users, learning, rag, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])