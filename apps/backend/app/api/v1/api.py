from fastapi import APIRouter

from app.api.v1.endpoints import auth, core_approve, reference, staging_metadata, staging_review, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(staging_metadata.router, prefix="/staging-metadata", tags=["Staging Metadata"])
api_router.include_router(staging_review.router, prefix="/staging-review", tags=["Staging Review"])
api_router.include_router(reference.router, prefix="/reference", tags=["Reference Data"])
api_router.include_router(core_approve.router, prefix="/core-approve", tags=["Core Approve"])
