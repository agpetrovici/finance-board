import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# parents[4]: logger/ -> utils/ -> backend/ -> app/ -> <project-root>
LOGS_DIR = Path(__file__).resolve().parents[4] / "logs" / "operations"

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

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    log_path = LOGS_DIR / f"{name}.log"
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
