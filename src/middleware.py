import time

import structlog
from fastapi import Request, Response
from structlog.contextvars import bind_contextvars, clear_contextvars

from custom_logging import configure_logger, logger

configure_logger()


async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    # These context vars will be added to all log entries emitted during the request
    request_id = request.headers.get("request-id")
    bind_contextvars(request_id=request_id)

    start_time = time.perf_counter_ns()

    try:
        response = await call_next(request)
    except Exception as exc:
        response = Response(status_code=500)
        structlog.get_logger("api.error").exception("Uncaught exception", exc_info=exc)
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code

    log_message = "Request completed"
    log_context = {
        "data": {
            "path": request.url.path,
            "method": request.method,
            "status_code": status_code,
            "process_time": process_time / 10**9,  # Convert to seconds
        }
    }

    if status_code == 200:
        logger.info(log_message, **log_context)
    elif status_code == 404:
        log_message = "Resource not found"
        logger.info(log_message, **log_context)
    elif status_code == 406:
        log_message = "Request not acceptable"
        logger.info(log_message, **log_context)

        response.headers["X-Process-Time"] = str(process_time / 10**9)

    return response
