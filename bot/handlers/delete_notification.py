from datetime import time
import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.common.utills import auth_user, tz_from_coords
from bot.enums.stickers import StickersEnum
from bot.states.notifications import NotificationFSM
from bot.keyboards.new_notification import (
    time_page_kb,
    sending_interval_page_kb,
    SelectedSendingInterval,
    SelectedTime,
    TimePage,
    MarkDone,
)
from bot.postgres.crud import (
    get_notification_templates_by_user,
    delete_notification_template,
)
from bot.keyboards.delete_notification import (
    NotificationTemplateCallback,
    delete_notification_kb,
)


router = Router()


@router.message(Command(commands=["delete_notification"]))
async def handle_delete_notification(
    message: Message,
    state: FSMContext,
) -> None:

    await state.clear()

    tg_id = str(message.from_user.id)

    user = await auth_user(
        message=message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        notification_templates = await get_notification_templates_by_user(
            user_id=user.user_id
        )

        if not notification_templates:
            await message.answer(
                text=(
                    "🤔 <b>Nothing to delete yet!</b>\n\n"
                    "✨ Create your first notification with /new_notification"
                ),
                parse_mode="HTML",
            )
            return

        text = "📋 <b>Your Notification Templates:</b>"

        await message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=delete_notification_kb(notification_templates),
        )


@router.callback_query(NotificationTemplateCallback.filter())
async def handle_delete_notification(
    callback_query: CallbackQuery,
    callback_data: NotificationTemplateCallback,
    state: FSMContext,
) -> None:

    await callback_query.answer()

    await state.clear()

    tg_id = str(callback_query.from_user.id)

    user = await auth_user(
        message=callback_query.message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        template_id = callback_data.template_id

        await delete_notification_template(notification_id=template_id)
        await callback_query.message.edit_text(
            text="🗑️ Notification deleted!",
            parse_mode="HTML",
        )
