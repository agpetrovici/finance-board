import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "logs", "operations")

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_loggers: dict[str, logging.Logger] = {}


def get_logger(
    name: str,
    console: bool = True,
) -> logging.Logger:
    """Return a named logger that writes to logs/operations/<name>.log (daily rotation).

    Args:
        name: Logical operation name used as the logger name and log filename.
        console: When True a StreamHandler is also attached so output appears in
                 stdout (useful for ETL scripts run from the terminal).
    """
    if name in _loggers:
        return _loggers[name]

    os.makedirs(LOGS_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    log_path = os.path.join(LOGS_DIR, f"{name}.log")
    file_handler = TimedRotatingFileHandler(
        log_path,
        when="midnight",
        backupCount=30,
        encoding="utf-8",
        utc=True,
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    _loggers[name] = logger
    return logger
