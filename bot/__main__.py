import asyncio

from bot.run import run_in_pooling
from bot.app import (
    get_bot,
    get_dispatcher,
)

from bot.config import settings
from bot.postgres.schema import Base
from bot.postgres.db import async_engine


async def create_postgres_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def main() -> None:
    """Entrypoint of the application"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_postgres_tables())

    bot = get_bot(token=settings.bot_client_token)
    dp = get_dispatcher(redis_host=settings.redis_host, redis_port=settings.redis_port)

    run_in_pooling(bot=bot, dp=dp)


if __name__ == "__main__":
    main()
