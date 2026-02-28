from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.handlers import setup_routers


async def set_commands(bot: Bot) -> None:
    """
    Set commands for bot.

    :param bot: Bot.
    """

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start from this"),
            BotCommand(command="new_notification", description="Create new notification"),
            BotCommand(command="delete_notification", description="Delete notification"),
        ]
    )


def setup_dispatcher(dispatcher: Dispatcher) -> None:
    """
    Setup dispatcher.

    :param dispatcher: Dispatcher.
    """
    pass
    # dispatcher.update.middleware(CustomMiddleware())
    # dispatcher.message.middleware(AntiFloodMiddleware())


async def setup_bot(bot: Bot, dispatcher: Dispatcher) -> None:

    await set_commands(bot)
    setup_routers(dispatcher)
    setup_dispatcher(dispatcher)
