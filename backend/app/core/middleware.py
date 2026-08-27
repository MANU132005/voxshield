import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("voxshield.access")


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that attaches a unique X-Request-ID header to incoming requests,
    logs request duration and status, and sets security response headers.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        t0 = time.perf_counter()

        # Sanitize incoming X-Request-ID or generate UUIDv4
        incoming_id = request.headers.get("X-Request-ID")
        if incoming_id and len(incoming_id) <= 64 and incoming_id.replace("-", "").isalnum():
            request_id = incoming_id
        else:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        t1 = time.perf_counter()
        duration_ms = round((t1 - t0) * 1000.0, 2)

        # Set security and correlation headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Latency: {duration_ms}ms"
        )

        return response
