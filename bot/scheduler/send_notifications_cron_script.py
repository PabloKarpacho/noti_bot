import asyncio
import random

from aiogram.exceptions import TelegramBadRequest

from bot.web.app import get_bot
from bot.common.logging import setup_logging, get_logger
from bot.config import settings
from bot.postgres.crud import (
    ensure_notifications_exist_for_templates,
    get_notification_templates_with_users,
    get_pending_notifications_by_template_ids,
    update_notification,
)
from bot.keyboards.new_notification import mark_notification_as_done_kb
from bot.enums.stickers import StickersEnum
from bot.scheduler.delivery import get_due_templates

logger = get_logger()

bot = get_bot(token=settings.bot_client_token)
SEND_CONCURRENCY = 10


async def _send_single_notification(notification, template, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            logger.info(
                "Sending notification {} to user {}",
                notification.notification_id,
                template.user.user_tg_id,
            )

            if not notification.sticker_sent:
                await bot.send_sticker(
                    chat_id=template.user.user_tg_id,
                    sticker=random.choice(StickersEnum.reminders_reply_list),
                )
                await update_notification(
                    notification_id=notification.notification_id, sticker_sent=True
                )

            if notification.last_bot_message_id is not None:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=template.user.user_tg_id,
                        message_id=notification.last_bot_message_id,
                        reply_markup=None,
                    )
                except TelegramBadRequest as e:
                    logger.error(
                        "Failed to edit message reply markup for notification {}: {}",
                        notification.notification_id,
                        e,
                    )

            message = await bot.send_message(
                chat_id=template.user.user_tg_id,
                text=template.message,
                reply_markup=mark_notification_as_done_kb(notification.notification_id),
            )
            await update_notification(
                notification_id=notification.notification_id,
                last_bot_message_id=message.message_id,
            )
        except TelegramBadRequest as e:
            logger.error(
                "Failed to send notification {} to user {}: {}",
                notification.notification_id,
                template.user.user_tg_id,
                e,
            )
        except Exception:
            logger.exception(
                "Unexpected error while sending notification {}",
                notification.notification_id,
            )


async def send_notifications():
    templates = await get_notification_templates_with_users()
    logger.info("Notification templates to evaluate: {}", len(templates))

    due_templates = get_due_templates(templates)
    logger.info("Templates due this minute: {}", len(due_templates))

    if not due_templates:
        return

    due_template_ids = [
        template.notification_template_id for template in due_templates
    ]
    template_by_id = {
        template.notification_template_id: template for template in due_templates
    }

    await ensure_notifications_exist_for_templates(due_template_ids)
    pending_notifications = await get_pending_notifications_by_template_ids(
        due_template_ids
    )
    logger.info("Pending notifications to send now: {}", len(pending_notifications))

    semaphore = asyncio.Semaphore(SEND_CONCURRENCY)
    await asyncio.gather(
        *[
            _send_single_notification(
                notification=notification,
                template=template_by_id[notification.template_id],
                semaphore=semaphore,
            )
            for notification in pending_notifications
            if notification.template_id in template_by_id
        ]
    )


async def main():
    setup_logging(level=settings.log_level)
    logger.info("Start send notifications cron script")
    await send_notifications()
    logger.info("Send notifications cron script finished")


if __name__ == "__main__":
    asyncio.run(main())
