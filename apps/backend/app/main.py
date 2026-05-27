from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def read_root():
    return {
        "message": "FastAPI backend is running"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
