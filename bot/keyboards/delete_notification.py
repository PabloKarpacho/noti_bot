from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from bot.postgres.schema import NotificationTemplate


class NotificationTemplateCallback(
    CallbackData,
    prefix="notification_template",  # type: ignore[call-arg]
):
    template_id: int
    template_name: str


def delete_notification_kb(temlates: list[NotificationTemplate]):

    kb = InlineKeyboardBuilder()

    # Кнопки времени
    for template in temlates:
        kb.button(
            text=f"✨{template.name}✨",
            callback_data=NotificationTemplateCallback(
                template_id=template.notification_template_id,
                template_name=template.name,
            ).pack(),
        )

    kb.adjust(1)

    return kb.as_markup()
