import logging
from sys import stdout
from pathlib import Path


def get_logger(name: str = "e2eLog", level: int = logging.DEBUG) -> logging.Logger:
    """
    Creates or retrieves a logger with a configurable logging level.
    Common levels: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        if level == logging.DEBUG:
            stream_handler = logging.StreamHandler(stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        log_path = Path("logs")
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / "automation.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


global_logger = get_logger(level=logging.DEBUG)
