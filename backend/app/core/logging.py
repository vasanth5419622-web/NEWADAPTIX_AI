import json
import logging
import time
from typing import Any, Dict, Optional

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add custom extra attributes if present
        for key in ["request_id", "step", "model", "status", "latency_ms", "confidence", "estimated_cost", "error"]:
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)
                
        return json.dumps(log_obj)

def setup_logger(name: str = "adaptix_farm") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()
