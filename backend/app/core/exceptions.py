import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("voxshield.exceptions")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    msg = exc.detail if isinstance(exc.detail, str) else "Request failed."
    logger.warning(f"[{request_id}] HTTP {exc.status_code}: {msg}")

    code_map = {
        400: "BAD_REQUEST",
        404: "NOT_FOUND",
        413: "PAYLOAD_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "UNPROCESSABLE_ENTITY",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    error_code = code_map.get(exc.status_code, "HTTP_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": msg,
            "error": {
                "code": error_code,
                "message": msg,
                "request_id": request_id
            }
        },
        headers={"X-Request-ID": request_id}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"[{request_id}] Validation error: {exc.errors()}")
    msg = "Input validation failed. Please check parameters."

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": msg,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": msg,
                "request_id": request_id
            }
        },
        headers={"X-Request-ID": request_id}
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled internal exception: {exc}", exc_info=True)
    msg = "An unexpected internal server error occurred. Please contact system support."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": msg,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": msg,
                "request_id": request_id
            }
        },
        headers={"X-Request-ID": request_id}
    )
