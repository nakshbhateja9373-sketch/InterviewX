from fastapi import APIRouter
from backend.app.config import settings
from backend.app.models import SystemHealthResponse

router = APIRouter(prefix="/api", tags=["System Health"])

@router.get("/health", response_model=SystemHealthResponse)
async def health_check():
    return SystemHealthResponse(
        status="healthy",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        ai_configured=settings.is_ai_configured,
        ai_model=settings.GEMINI_MODEL,
        environment=settings.ENVIRONMENT
    )
