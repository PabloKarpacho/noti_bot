"""Bot handlers"""

from aiogram import Dispatcher

from bot.common.logging import get_logger
from bot.handlers.start import router as start_router
from bot.handlers.register import router as register_router
from bot.handlers.add_notification import router as add_notification_router
from bot.handlers.delete_notification import router as delete_notification_router

logger = get_logger()


def setup_routers(dispatcher: Dispatcher) -> None:
    """
    Add routers in dispatcher.

    :param dispatcher: Main dispatcher of routers.
    """
    logger.info("Registering bot routers")
    dispatcher.include_router(start_router)
    dispatcher.include_router(register_router)
    dispatcher.include_router(add_notification_router)
    dispatcher.include_router(delete_notification_router)
    logger.info("All bot routers registered")
