import asyncio

from bot.run import run_in_pooling
from bot.app import (
    get_bot,
    get_dispatcher,
)

from bot.config import settings
from bot.common.logging import setup_logging, get_logger
from bot.postgres.schema import Base
from bot.postgres.db import async_engine

logger = get_logger()


async def create_postgres_tables() -> None:
    logger.info("Creating PostgreSQL tables (if not exists)")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL tables are ready")


def main() -> None:
    """Entrypoint of the application"""

    setup_logging(level=settings.log_level)
    logger.info("Starting bot application")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_postgres_tables())

    bot = get_bot(token=settings.bot_client_token)
    dp = get_dispatcher(redis_host=settings.redis_host, redis_port=settings.redis_port)

    logger.info("Bot and dispatcher are initialized, starting polling")
    run_in_pooling(bot=bot, dp=dp)


if __name__ == "__main__":
    main()
