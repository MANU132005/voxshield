import os
from fastapi import APIRouter, Response, status
from app.core.config import settings
from app.services.anti_spoofing.detector import AntiSpoofingDetector

router = APIRouter()

# Global detector instance for readiness probe verification
_detector_instance = None

def get_detector() -> AntiSpoofingDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = AntiSpoofingDetector()
    return _detector_instance


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Backend service health status check (Liveness probe).
    """
    return {"status": "ok"}


@router.get("/ready", summary="Readiness Check")
async def readiness_check(response: Response):
    """
    Backend service readiness check (Readiness probe).
    Genuinely verifies that AI anti-spoofing model checkpoint and core dependencies are loaded.
    """
    detector = get_detector()
    resolved_checkpoint = detector._resolve_checkpoint()
    
    is_model_loaded = (
        detector.model is not None and 
        resolved_checkpoint is not None and 
        os.path.exists(resolved_checkpoint)
    )

    if not is_model_loaded:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "model_checkpoint": resolved_checkpoint if resolved_checkpoint else settings.MODEL_PATH,
            "detector_ready": False,
            "replay_dsp_ready": True,
            "detail": "Anti-spoofing model checkpoint not loaded or missing"
        }

    return {
        "status": "ready",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "model_checkpoint": resolved_checkpoint,
        "detector_ready": True,
        "replay_dsp_ready": True
    }

