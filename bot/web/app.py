from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot.common.logging import get_logger

logger = get_logger()


def get_bot(token: str) -> Bot:
    """
    Initializes and returns a Bot instance with the given token.

    :param token: API token for the bot.
    """
    logger.debug("Initializing Telegram Bot instance for web/scheduler context")
    return Bot(token=token)


def get_dispatcher(redis_host: str, redis_port: str) -> Dispatcher:
    """
    Initializes and returns a Dispatcher instance.

    """

    redis_url = f"redis://{redis_host}:{redis_port}"
    logger.debug("Initializing Dispatcher with Redis storage: {}", redis_url)
    storage = RedisStorage.from_url(redis_url)

    return Dispatcher(storage=storage)
