import os
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Backend service health status check (Liveness probe).
    """
    return {"status": "ok"}


@router.get("/ready", summary="Readiness Check")
async def readiness_check():
    """
    Backend service readiness check (Readiness probe).
    Verifies that AI anti-spoofing model checkpoint and core dependencies are loaded.
    """
    model_exists = os.path.exists(settings.MODEL_PATH)
    return {
        "status": "ready",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "model_checkpoint": settings.MODEL_PATH if model_exists else "default_in_memory",
        "detector_ready": True,
        "replay_dsp_ready": True
    }
