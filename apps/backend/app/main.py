from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exception_handlers import app_exception_handler
from app.core.exceptions import AppException
from app.integrations.elasticsearch import get_elasticsearch_client

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

es_client = get_elasticsearch_client()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def read_root():
    return {
        "message": "FastAPI backend is running"
    }

if settings.DEBUG:
    @app.get("/health-elastic", include_in_schema=False)
    def check_connection():
        info = es_client.info()
        return {
            "status": "ok",
            "cluster_name": info["cluster_name"],
            "version": info["version"]["number"],
        }


@app.get("/health")
def health_check():
    return {"status": "ok"}
