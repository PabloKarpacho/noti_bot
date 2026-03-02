import asyncio

from aiogram import Bot, Dispatcher

from bot.common.logging import get_logger
from bot.setup_bot import setup_bot

logger = get_logger()


def run_in_pooling(bot: Bot, dp: Dispatcher) -> None:

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        logger.info("Deleting webhook before polling")

        loop.run_until_complete(
            bot.delete_webhook(),
        )

        logger.info("Setting up bot and dispatcher")
        loop.run_until_complete(
            setup_bot(
                bot=bot,
                dispatcher=dp,
            ),
        )

        logger.info("Start polling")
        loop.run_until_complete(dp.start_polling(bot))
    except Exception:
        logger.exception("Unhandled exception in polling loop")
        raise
    finally:
        logger.info("Closing polling event loop")
        loop.close()
