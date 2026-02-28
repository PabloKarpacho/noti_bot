from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage


def get_bot(token: str) -> Bot:
    """
    Initializes and returns a Bot instance with the given token.

    :param token: API token for the bot.
    """

    return Bot(token=token)


def get_dispatcher(redis_host: str, redis_port: str) -> Dispatcher:
    """
    Initializes and returns a Dispatcher instance.

    """


    storage = RedisStorage.from_url(f"redis://{redis_host}:{redis_port}")

    return Dispatcher(storage=storage)