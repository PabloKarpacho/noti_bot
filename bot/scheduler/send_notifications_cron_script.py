import asyncio
from loguru import logger
import random

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram.exceptions import TelegramBadRequest


from bot.web.app import get_bot
from bot.config import settings
from bot.postgres.crud import get_pending_notifications
from bot.postgres.schema import NotificationTemplate
from bot.keyboards.new_notification import mark_notification_as_done_kb
from bot.enums.stickers import StickersEnum

bot = get_bot(token=settings.bot_client_token)


def should_send_notification(notification_template: NotificationTemplate) -> bool:
    logger.info(f"Checking if we should send notification")
    tz = ZoneInfo(notification_template.user.timezone)
    interval = notification_template.sending_interval_minutes

    if not interval or interval <= 0:
        return False

    # "сейчас" в TZ пользователя, округляем до минуты
    now_dt = datetime.now(tz=tz).replace(second=0, microsecond=0)
    today = now_dt.date()

    # Старт/стоп как aware datetime в той же TZ
    start_dt = datetime.combine(
        today, notification_template.time_start, tzinfo=tz
    ).replace(second=0, microsecond=0)
    stop_dt = datetime.combine(
        today, notification_template.time_stop, tzinfo=tz
    ).replace(second=0, microsecond=0)

    # Если окно "переливается" через полночь (например 23:00 -> 02:30)
    if stop_dt < start_dt:
        stop_dt += timedelta(days=1)
        # если сейчас уже после полуночи (00:xx..), то "сейчас" относится к следующему дню относительно start_dt
        if now_dt < start_dt:
            now_dt += timedelta(days=1)

    # Вне окна — не отправляем
    if not (start_dt <= now_dt <= stop_dt):
        return False

    # Проверяем попадание в сетку интервала
    minutes_from_start = int((now_dt - start_dt).total_seconds() // 60)

    check_result = minutes_from_start % interval == 0

    logger.info(
        f"Check result for notification {notification_template.notification_template_id}: {check_result}"
    )

    return check_result


async def send_notifications():

    pending_notifications = await get_pending_notifications()

    for notification in pending_notifications:

        try:
            notification_teamplate = notification.template

            if should_send_notification(notification_teamplate):

                logger.info(
                    f"Sending notification {notification.notification_id} to user {notification_teamplate.user.user_tg_id}"
                )

                await bot.send_sticker(
                    chat_id=notification_teamplate.user.user_tg_id,
                    sticker=random.choice(StickersEnum.reminders_reply_list),
                )

                await bot.send_message(
                    chat_id=notification_teamplate.user.user_tg_id,
                    text=notification_teamplate.message,
                    reply_markup=mark_notification_as_done_kb(notification.notification_id),
                )
        except TelegramBadRequest as e:
            logger.error(
                f"Failed to send notification {notification.notification_id} to user {notification_teamplate.user.user_tg_id}: {e}"
            )


async def main():
    await send_notifications()


if __name__ == "__main__":
    asyncio.run(main())
