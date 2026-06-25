from fastapi import APIRouter

from app.api.v1.endpoints import (
    backup,
    auth,
    core_approve,
    core_repository,
    logs,
    reference,
    reports,
    search,
    staging_metadata,
    staging_review,
    users,
    notification
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

api_router.include_router(
    staging_metadata.router,
    prefix="/staging-metadata",
    tags=["Staging Metadata"]
)

api_router.include_router(
    staging_review.router,
    prefix="/staging-review",
    tags=["Staging Review"]
)

api_router.include_router(reference.router, prefix="/reference", tags=["Reference Data"])
api_router.include_router(core_approve.router, prefix="/core-approve", tags=["Core Approve"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(core_repository.router, prefix="/core-repository", tags=["Core Repository"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(backup.router, prefix="/backup", tags=["Backup"])

api_router.include_router(
    notification.router,
    prefix="/notifications",
    tags=["Notifications"]
)