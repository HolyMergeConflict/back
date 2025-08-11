import logging
import sys
import json
import time
from opentelemetry.trace import get_current_span

class JsonFormatter(logging.Formatter):
    def format(self, record):
        span = get_current_span()
        span_context = span.get_span_context() if span else None
        trace_id = None
        span_id = None
        if span_context and span_context.is_valid:
            trace_id = format(span_context.trace_id, "032x")
            span_id = format(span_context.span_id, "016x")

        log_obj = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": trace_id,
            "span_id": span_id,
            "service": "reco-api",
        }
        return json.dumps(log_obj, ensure_ascii=False)

def setup_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger