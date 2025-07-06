# my_logger.py
import logging
import os
from datetime import datetime
import contextvars

# def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    # """
    # Set up and return a logger with the given name and optional log file.
    # """
    # logger = logging.getLogger(name)
    # logger.setLevel(level)

    # # Avoid duplicate log entries
    # if logger.handlers:
    #     return logger

    # # Create log formatter
    # formatter = logging.Formatter(
    #     '%(levelname)s: - %(asctime)s - %(name)s - %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S'
    # )

    # # Console handler
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    # # File handler (optional)
    # if log_file:
    #     # Ensure log directory exists
    #     os.makedirs(os.path.dirname(log_file), exist_ok=True)
    #     file_handler = logging.FileHandler(log_file)
    #     file_handler.setFormatter(formatter)
    #     logger.addHandler(file_handler)

    # return logger

# Context variable (define here or import from another context module)
request_id_var = contextvars.ContextVar("request_id", default="-")

class ContextFilter(logging.Filter):
    def filter(self, record):
        # Attach context variable value to the log record
        record.request_id = request_id_var.get()
        return True

def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Set up and return a logger with the given name and optional log file.
    Injects context variables like request_id into logs.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Include request_id in format
    formatter = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(name)s - [Request-ID: %(request_id)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add the context filter
    logger.addFilter(ContextFilter())

    return logger