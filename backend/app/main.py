from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.aws import router as aws_router
from app.api.connect import router as connect_router
from app.api.dashboard import router as dashboard_router
from app.api.finops import router as finops_router
from app.api.health import router as health_router
from app.api.resources import router as resources_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(aws_router)
app.include_router(resources_router)
app.include_router(finops_router)
app.include_router(connect_router)
app.include_router(dashboard_router)
app.include_router(ai_router)
app.include_router(audit_router)
