import logging
import sys
from typing import Union
import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.requests import Request
from starlette.responses import Response


logger = structlog.stdlib.get_logger() 

class DpLogger:
    def __init__(self, namespace="idpd-api-poc"):
        self.namespace = namespace

    def log(self, event, level, data=None):
        trace_id = generate_trace_id()
        span_id = generate_span_id()

        severity = {
            "debug": 3,  # INFO
            "warning": 2,  # WARNING
            "error": 1,  # ERROR
        }.get(level, 3)  # Default to INFO

        log_entry = {
            "namespace": self.namespace,
            "event": event,
            "trace_id": trace_id,
            "span_id": span_id,
            "severity": severity,
            "data": data if data is not None else {},
        }

        logger.log(level, **{"event_dict": log_entry})

    def debug(self, event, data=None):
        self.log(event, "debug", data)

    def warning(self, event, data=None):
        self.log(event, "warning", data)

    def error(self, event, data=None):
        self.log(event, "error", data)

def generate_trace_id():
    return "your_trace_id"

def generate_span_id():
    return "your_span_id"


def configure_logger(enable_json_logs: bool = False):
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

    shared_processors = [
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.THREAD,
                structlog.processors.CallsiteParameter.THREAD_NAME,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
            }
        ),
        structlog.stdlib.ExtraAdder(),
    ]

    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logs_render = (
        structlog.processors.JSONRenderer()
        if enable_json_logs
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    _configure_default_logging_by_custom(shared_processors, logs_render)

def _configure_default_logging_by_custom(shared_processors, logs_render):
    handler = logging.StreamHandler()
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            _extract_from_record,
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            logs_render,
        ],
    )
    handler.setFormatter(formatter)
    root_uvicorn_logger = logging.getLogger()
    root_uvicorn_logger.addHandler(handler)
    root_uvicorn_logger.setLevel(logging.INFO)

def _extract_from_record(_, __, event_dict):
    record = event_dict["_record"]
    event_dict["thread_name"] = record.threadName
    event_dict["process_name"] = record.processName
    return event_dict


# Define a function to create a log event with the specified structure
def create_log_event(
    event: str,
    severity: str,
    http_data: dict = None,
    auth_data: dict = None,
    errors: list = None,
    raw: str = None,
    data: dict = None,
):
    # Create a log event following the specified structure
    log_event = {
        "namespace": "your-service-name",
        "event": event,
        "severity": severity,
    }

    if http_data:
        log_event["http"] = http_data
    if auth_data:
        log_event["auth"] = auth_data
    if errors:
        log_event["errors"] = errors
    if raw:
        log_event["raw"] = raw
    if data:
        log_event["data"] = data

    logger.info(**log_event)

# Handle uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Log any uncaught exception instead of letting it be printed by Python
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.RootLogger.error(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )

    log_event = create_log_event(
        event="Uncaught exception",
        severity="ERROR",
        errors=[{"message": str(exc_value)}],
    )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception