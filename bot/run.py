import asyncio

from aiogram import Bot, Dispatcher
from aiohttp import web

from bot.common.logging import get_logger
from bot.setup_bot import setup_bot
from bot.config import settings
from bot.web.alice import create_alice_app

logger = get_logger()


def run_in_pooling(bot: Bot, dp: Dispatcher) -> None:

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    runner = None

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

        if settings.alice_webhook_secret:
            runner = web.AppRunner(create_alice_app(bot, settings.alice_webhook_secret))
            loop.run_until_complete(runner.setup())
            loop.run_until_complete(web.TCPSite(runner, "0.0.0.0", 8000).start())
            logger.info("Alice webhook is listening on port 8000")

        logger.info("Start polling")
        loop.run_until_complete(dp.start_polling(bot))
    except Exception:
        logger.exception("Unhandled exception in polling loop")
        raise
    finally:
        if runner is not None:
            loop.run_until_complete(runner.cleanup())
        logger.info("Closing polling event loop")
        loop.close()
