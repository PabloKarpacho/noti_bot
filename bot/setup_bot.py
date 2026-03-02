from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.common.logging import get_logger
from bot.handlers import setup_routers

logger = get_logger()


async def set_commands(bot: Bot) -> None:
    """
    Set commands for bot.

    :param bot: Bot.
    """

    logger.info("Setting bot commands")
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start from this"),
            BotCommand(
                command="new_notification", description="Create new notification"
            ),
            BotCommand(
                command="delete_notification", description="Delete notification"
            ),
        ]
    )


def setup_dispatcher(dispatcher: Dispatcher) -> None:
    """
    Setup dispatcher.

    :param dispatcher: Dispatcher.
    """
    logger.debug("Configuring dispatcher middleware")
    pass
    # dispatcher.update.middleware(CustomMiddleware())
    # dispatcher.message.middleware(AntiFloodMiddleware())


async def setup_bot(bot: Bot, dispatcher: Dispatcher) -> None:
    logger.info("Setup bot started")
    await set_commands(bot)
    setup_routers(dispatcher)
    setup_dispatcher(dispatcher)
    logger.info("Setup bot finished")
