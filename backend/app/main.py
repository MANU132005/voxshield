import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.middleware import RequestCorrelationMiddleware
from app.core.rate_limiter import InMemoryRateLimiter
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler
)
from app.api.routes import api_router

# Configure Application Logger
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "VoxShield is a production-grade AI-powered Voice Impersonation, Deepfake Audio, "
        "and Acoustic Replay Attack Detection API. It ingests multi-format audio (.wav, .mp3, .flac), "
        "extracts 80-channel Log-Mel Spectrograms and 20-channel LFCC features, executes 2D Residual Convolutional "
        "Anti-Spoofing Neural Inference and Single-STFT Acoustic Replay DSP Analysis, and outputs a 6-layer "
        "explainable security risk assessment with structured machine-readable evidence items."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# 1. Register Global Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# 2. Register Request Correlation & Access Middleware
app.add_middleware(RequestCorrelationMiddleware)

# 3. Register In-Memory Rate Limiter Middleware
app.add_middleware(
    InMemoryRateLimiter,
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS
)

# 4. Configure Secure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Retry-After"]
)

# 5. Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", summary="Root Endpoint")
async def root():
    return {
        "message": "Welcome to VoxShield AI Audio Security API",
        "version": settings.VERSION,
        "commit": "114cbff",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health",
        "ready": f"{settings.API_V1_STR}/ready"
    }


@app.get("/health", summary="Global Health Probe")
async def global_health():
    """
    Root level health probe endpoint returning {"status": "ok"}.
    """
    return {"status": "ok"}


@app.get("/openapi.json", summary="Root OpenAPI Spec Alias", include_in_schema=False)
async def openapi_alias():
    return app.openapi()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
