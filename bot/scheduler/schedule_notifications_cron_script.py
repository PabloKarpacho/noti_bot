import asyncio
from typing import List

from bot.common.logging import setup_logging, get_logger
from bot.config import settings

from bot.postgres.schema import NotificationTemplate
from bot.postgres.crud import get_notification_templates, create_notification

logger = get_logger()


async def _get_notification_templates() -> List[NotificationTemplate]:
    logger.debug("Loading notification templates")

    notification_templates = await get_notification_templates()

    logger.info("Loaded {} notification templates", len(notification_templates))

    return notification_templates


async def _schedule_notifications(
    notification_templates: List[NotificationTemplate],
):

    if not notification_templates:
        logger.info("No notification templates found, skip scheduling")
        return

    logger.info(
        "Scheduling notifications for {} templates", len(notification_templates)
    )
    for notification_template in notification_templates:
        await create_notification(
            template_id=notification_template.notification_template_id,
            marked_as_done=False,
        )
    logger.info("Scheduling notifications finished")


async def main():
    setup_logging(level=settings.log_level)
    logger.info("Start schedule notifications cron script")
    notification_templates = await _get_notification_templates()

    await _schedule_notifications(notification_templates=notification_templates)
    logger.info("Schedule notifications cron script finished")


if __name__ == "__main__":
    asyncio.run(main())
