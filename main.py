from bot.common.logging import get_logger, setup_logging
from bot.config import settings


def main():
    setup_logging(level=settings.log_level)
    logger = get_logger()
    logger.info("noti-bot main entrypoint started")


if __name__ == "__main__":
    main()
