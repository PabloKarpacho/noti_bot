import asyncio
from typing import List


from bot.postgres.schema import NotificationTemplate
from bot.postgres.crud import get_notification_templates, create_notification



async def _get_notification_templates() -> List[NotificationTemplate]:

    notification_templates = await get_notification_templates()

    return notification_templates


async def _schedule_notifications(
    notification_templates: List[NotificationTemplate],
):

    if not notification_templates:
        return

    for notification_template in notification_templates:
        await create_notification(
            template_id=notification_template.notification_template_id,
            marked_as_done=False,
        )


async def main():
    notification_templates = await _get_notification_templates()

    await _schedule_notifications(notification_templates=notification_templates)


if __name__ == "__main__":
    asyncio.run(main())
