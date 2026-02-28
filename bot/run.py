import asyncio

from aiogram import Bot, Dispatcher

from bot.setup_bot import setup_bot


def run_in_pooling(bot: Bot, dp: Dispatcher) -> None:

    try:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(
            bot.delete_webhook(),
        )

        loop.run_until_complete(
            setup_bot(
                bot=bot,
                dispatcher=dp,
            ),
        )

        loop.run_until_complete(dp.start_polling(bot))
    except Exception as e:
        raise
    finally:
        loop.close()
