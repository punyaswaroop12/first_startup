from fastapi import APIRouter

from app.api.routes import (
    admin,
    auth,
    automations,
    chat,
    dashboard,
    documents,
    microsoft,
    reports,
    tags,
)

api_router = APIRouter()
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(microsoft.router, prefix="/admin/microsoft", tags=["admin-microsoft"])
api_router.include_router(automations.router, prefix="/automations", tags=["automations"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
