from bot.run import run_in_pooling
from bot.app import (
    get_bot,
    get_dispatcher,
)

from bot.config import settings
from bot.common.logging import setup_logging, get_logger

logger = get_logger()


def main() -> None:
    """Entrypoint of the application"""

    setup_logging(level=settings.log_level)
    logger.info("Starting bot application")

    bot = get_bot(token=settings.bot_client_token)
    dp = get_dispatcher(redis_host=settings.redis_host, redis_port=settings.redis_port)

    logger.info("Bot and dispatcher are initialized, starting polling")
    run_in_pooling(bot=bot, dp=dp)


if __name__ == "__main__":
    main()
