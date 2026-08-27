import time
import math
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


class InMemoryRateLimiter(BaseHTTPMiddleware):
    """
    Sliding window in-memory rate limiting middleware.
    Enforces RATE_LIMIT_REQUESTS per RATE_LIMIT_WINDOW_SECONDS per client IP.
    Returns HTTP 429 Too Many Requests with Retry-After header when exceeded.
    """
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_store: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Exclude health and OpenAPI docs from rate limiting
        path = request.url.path
        if path.endswith("/health") or path.endswith("/ready") or "docs" in path or "openapi" in path:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        timestamps = self.requests_store[client_ip]
        # Remove timestamps outside the sliding window
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
        self.requests_store[client_ip] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            oldest_timestamp = valid_timestamps[0]
            retry_after = math.ceil(self.window_seconds - (now - oldest_timestamp))
            request_id = getattr(request.state, "request_id", "unknown")

            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds}s allowed.",
                        "request_id": request_id
                    }
                },
                headers={
                    "Retry-After": str(max(retry_after, 1)),
                    "X-Request-ID": request_id
                }
            )

        self.requests_store[client_ip].append(now)
        return await call_next(request)
