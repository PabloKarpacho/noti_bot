import sys

from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=level.upper(),
        backtrace=True,
        diagnose=False,
        enqueue=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )


def get_logger():
    return logger
