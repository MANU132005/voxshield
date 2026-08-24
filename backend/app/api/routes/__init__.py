from fastapi import APIRouter
from app.api.routes import health, analyze, stream

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(analyze.router, tags=["Audio Security Analysis"])
api_router.include_router(stream.router, tags=["Real-time WebSocket Stream"])
