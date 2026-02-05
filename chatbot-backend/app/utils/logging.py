import logging
import json
from datetime import datetime

import contextvars

# Context variable for request ID
request_id_var = contextvars.ContextVar('request_id', default=None)

class JSONFormatter(logging.Formatter):
    """
    Formats log records as a JSON string.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        request_id = request_id_var.get()
        if request_id:
            log_record["request_id"] = request_id
            
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
            
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)


def setup_logging():
    """
    Sets up structured JSON logging for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        
    handler = logging.StreamHandler()
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Silence other loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Call setup_logging() to apply the configuration when this module is imported.
setup_logging()
