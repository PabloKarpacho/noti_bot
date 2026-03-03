from datetime import time
import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.common.utills import auth_user, tz_from_coords
from bot.common.logging import get_logger
from bot.enums.stickers import StickersEnum
from bot.states.notifications import NotificationFSM
from bot.keyboards.new_notification import (
    time_page_kb,
    sending_interval_page_kb,
    build_save_notification_kb,
    SelectedSendingInterval,
    SelectedTime,
    TimePage,
    MarkDone,
    SaveNotification,
)
from bot.postgres.crud import (
    create_notification_template,
    update_notification,
    get_notification_templates_by_user,
    update_user,
)
from bot.scheduler.schedule_notifications_cron_script import _schedule_notifications

router = Router()
logger = get_logger()


@router.message(Command(commands=["new_notification"]))
async def handle_new_notification(
    message: Message,
    state: FSMContext,
) -> None:
    logger.info("Received /new_notification from user_tg_id={}", message.from_user.id)

    await state.clear()

    tg_id = str(message.from_user.id)

    user = await auth_user(
        message=message,
        tg_id=tg_id,
        state=state,
    )

    if user:
        await message.answer(
            text=(
                "📝 <b>Create a New Notification</b>\n\n"
                "Please send the <b>name</b> for your new notification."
            ),
            parse_mode="HTML",
        )

        await state.set_state(NotificationFSM.create_name)


@router.message(NotificationFSM.create_name)
async def handle_create_notification_name(
    message: Message,
    state: FSMContext,
) -> None:
    logger.debug("Received notification name from user_tg_id={}", message.from_user.id)

    await state.clear()

    tg_id = str(message.from_user.id)

    user = await auth_user(
        message=message,
        tg_id=tg_id,
        state=state,
    )

    if user:
        await message.answer(
            text=(
                "📝 <b>Create a New Notification</b>\n\n"
                "Please send the <b>text</b> for your new notification."
            ),
            parse_mode="HTML",
        )

        await state.set_state(NotificationFSM.create_message)

        await state.update_data(
            notification_name=message.text,
        )


@router.message(NotificationFSM.create_message)
async def handle_create_notification_message(
    message: Message,
    state: FSMContext,
) -> None:
    logger.debug(
        "Received notification message from user_tg_id={}", message.from_user.id
    )

    data = await state.get_data()

    await state.clear()

    tg_id = str(message.from_user.id)

    user = await auth_user(
        message=message,
        tg_id=tg_id,
        state=state,
    )

    if user:
        await message.answer(
            text=(
                "⏰ <b>Select Start Time</b>\n\n"
                "Please choose the time when your notification should begin."
            ),
            parse_mode="HTML",
            reply_markup=time_page_kb(
                page=0, per_page=9, step_min=30, start_h=0, end_h=23
            ),
        )

        await state.set_state(NotificationFSM.create_start_time)

        await state.update_data(
            notification_name=data.get("notification_name"),
            notification_message=message.text,
        )


@router.callback_query(NotificationFSM.create_start_time, SelectedTime.filter())
async def handle_create_notification_start_time(
    callback_query: CallbackQuery,
    state: FSMContext,
    callback_data: SelectedTime,
) -> None:
    logger.debug(
        "Received start time callback from user_tg_id={} time={:02d}:{:02d}",
        callback_query.from_user.id,
        callback_data.hour,
        callback_data.minute,
    )

    await callback_query.answer()

    data = await state.get_data()

    await state.clear()

    tg_id = str(callback_query.from_user.id)

    user = await auth_user(
        message=callback_query.message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        chosen = f"{callback_data.hour}:{callback_data.minute}"

        await callback_query.message.answer(f"⏰ You chose: {chosen}")

        await callback_query.message.answer(
            text=(
                "⏰ <b>Select End Time</b>\n\n"
                "Please choose the time when your notification should end."
            ),
            parse_mode="HTML",
            reply_markup=time_page_kb(
                page=0,
                per_page=9,
                step_min=30,
                start_h=callback_data.hour,
                start_m=callback_data.minute,
                end_h=23,
                time_type="time_end",
            ),
        )
        await state.set_state(NotificationFSM.create_end_time)

        await state.update_data(
            notification_name=data.get("notification_name"),
            notification_message=data.get("notification_message"),
            notification_start_time_hour=callback_data.hour,
            notification_start_time_minute=callback_data.minute,
        )


@router.callback_query(NotificationFSM.create_end_time, SelectedTime.filter())
async def handle_create_notification_end_time(
    callback_query: CallbackQuery,
    state: FSMContext,
    callback_data: SelectedTime,
) -> None:
    logger.debug(
        "Received end time callback from user_tg_id={} time={:02d}:{:02d}",
        callback_query.from_user.id,
        callback_data.hour,
        callback_data.minute,
    )
    await callback_query.answer()

    data = await state.get_data()

    await state.clear()

    tg_id = str(callback_query.from_user.id)

    user = await auth_user(
        message=callback_query.message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        chosen = f"{callback_data.hour}:{callback_data.minute}"

        await callback_query.message.answer(f"⏰ You chose: {chosen}")

        await callback_query.message.answer(
            text=(
                "⏰ <b>Select Sending Interval</b>\n\n"
                "Please choose the interval in minutes for sending your notification."
            ),
            parse_mode="HTML",
            reply_markup=sending_interval_page_kb(
                page=0,
                per_page=9,
                step_min=5,
            ),
        )

        await state.set_state(NotificationFSM.create_sending_interval_minutes)

        await state.update_data(
            notification_name=data.get("notification_name"),
            notification_message=data.get("notification_message"),
            notification_start_time_hour=data.get("notification_start_time_hour"),
            notification_start_time_minute=data.get("notification_start_time_minute"),
            notification_end_time_hour=callback_data.hour,
            notification_end_time_minute=callback_data.minute,
        )


@router.callback_query(
    NotificationFSM.create_sending_interval_minutes, SelectedSendingInterval.filter()
)
async def handle_create_notification_sending_interval_minutes(
    callback_query: CallbackQuery,
    state: FSMContext,
    callback_data: SelectedSendingInterval,
) -> None:
    logger.debug(
        "Received interval callback from user_tg_id={} minutes={}",
        callback_query.from_user.id,
        callback_data.minutes,
    )

    await callback_query.answer()

    data = await state.get_data()

    await state.clear()

    tg_id = str(callback_query.from_user.id)

    user = await auth_user(
        message=callback_query.message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        chosen = f"{callback_data.minutes:02d}"

        await callback_query.message.answer(f"⏰ You chose: {chosen}")

        if user.timezone is None:
            logger.info("User {} has no timezone, requesting location", user.user_id)

            await callback_query.message.answer(
                text=(
                    "📍 <b>Timezone Detection</b>\n\n"
                    "Please share your location so I can automatically determine "
                    "your timezone ⏰"
                ),
                parse_mode="HTML",
            )

            await state.update_data(
                notification_name=data.get("notification_name"),
                notification_message=data.get("notification_message"),
                notification_start_time_hour=data.get("notification_start_time_hour"),
                notification_start_time_minute=data.get(
                    "notification_start_time_minute"
                ),
                notification_end_time_hour=data.get("notification_end_time_hour"),
                notification_end_time_minute=data.get("notification_end_time_minute"),
                notification_sending_interval_minutes=callback_data.minutes,
            )

            return

        await state.set_state(NotificationFSM.save_notification)

        await callback_query.message.answer(
            text=("💾 <b>Click button to save notification</b>"),
            parse_mode="HTML",
            reply_markup=build_save_notification_kb(),
        )

        await state.update_data(
            notification_name=data.get("notification_name"),
            notification_message=data.get("notification_message"),
            notification_start_time_hour=data.get("notification_start_time_hour"),
            notification_start_time_minute=data.get("notification_start_time_minute"),
            notification_end_time_hour=data.get("notification_end_time_hour"),
            notification_end_time_minute=data.get("notification_end_time_minute"),
            notification_sending_interval_minutes=callback_data.minutes,
        )


@router.callback_query(NotificationFSM.save_notification, SaveNotification.filter())
async def handle_save_notification(
    callback_query: CallbackQuery, state: FSMContext, callback_data: SaveNotification
):
    logger.info("Saving notification for user_tg_id={}", callback_query.from_user.id)
    await callback_query.answer()

    data = await state.get_data()

    await state.clear()

    tg_id = str(callback_query.from_user.id)

    user = await auth_user(
        message=callback_query.message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        time_start = time(
            hour=data.get("notification_start_time_hour"),
            minute=data.get("notification_start_time_minute"),
        )

        if data.get("notification_end_time_hour") is None or data.get("notification_end_time_minute") is None:
            time_end = None
        else:
            time_end = time(
                hour=data.get("notification_end_time_hour"),
                minute=data.get("notification_end_time_minute"),
            )

        notification_template = await create_notification_template(
            user_id=user.user_id,
            name=data.get("notification_name"),
            message=data.get("notification_message"),
            time_start=time_start,
            sending_interval_minutes=data.get("notification_sending_interval_minutes"),
            time_stop=time_end,
        )
        logger.info(
            "Notification template {} created for user_id={}",
            notification_template.notification_template_id,
            user.user_id,
        )

        await _schedule_notifications([notification_template])

        await callback_query.message.answer(
            text=(
                "🎉 <b>Notification Created Successfully!</b>\n\n"
                "Your notification has been saved and is ready to go 🚀"
            ),
            parse_mode="HTML",
        )


@router.message(F.location)
async def handle_update_or_create_location(message: Message, state: FSMContext):
    logger.info("Received location from user_tg_id={}", message.from_user.id)

    tg_id = str(message.from_user.id)

    user = await auth_user(
        message=message,
        tg_id=tg_id,
        state=state,
    )

    if user:

        tz = tz_from_coords(
            lat=message.location.latitude,
            lon=message.location.longitude,
        )

        if not tz:
            logger.warning("Failed to detect timezone for user_tg_id={}", tg_id)
            await message.answer(
                text=(
                    "⚠️ <b>Couldn't detect your timezone.</b>\n\n"
                    "Please try sending your location again 📍"
                ),
                parse_mode="HTML",
            )
            return

        await update_user(user_id=user.user_id, timezone=tz)
        logger.info("Updated timezone for user_id={} tz={}", user.user_id, tz)

        if user.timezone is not None:
            await message.answer(
                text=(
                    "✅ <b>Timezone Updated!</b>\n\n"
                    f"Your new timezone: <b>{tz}</b> ⏰"
                ),
                parse_mode="HTML",
            )
        else:
            await message.answer(
                text=("✅ <b>Timezone Saved!</b>\n\n" f"Your timezone: <b>{tz}</b> ⏰"),
                parse_mode="HTML",
            )
            await state.set_state(NotificationFSM.save_notification)

            await message.answer(
                text=("💾 <b>Click button to save notification</b>"),
                parse_mode="HTML",
                reply_markup=build_save_notification_kb(),
            )


@router.callback_query(MarkDone.filter())
async def handle_mark_done(callback_query: CallbackQuery, callback_data: MarkDone):
    await callback_query.answer()
    if callback_data.is_done:
        notification_id = callback_data.notification_id
        logger.info(
            "Marking notification as done notification_id={} user_tg_id={}",
            notification_id,
            callback_query.from_user.id,
        )

        await update_notification(notification_id=notification_id, marked_as_done=True)
        await callback_query.message.edit_text("Good job! ✅")

        await callback_query.message.answer_sticker(
            sticker=random.choice(StickersEnum.mark_as_done_reply_list),
        )


@router.callback_query(TimePage.filter())
async def paginate_time(
    callback: CallbackQuery, state: FSMContext, callback_data: TimePage
):

    await callback.answer()

    data = await state.get_data()

    current_state = await state.get_state()

    page = callback_data.page

    if current_state == NotificationFSM.create_start_time.state:

        await callback.message.edit_reply_markup(
            reply_markup=time_page_kb(
                page=page, per_page=9, step_min=30, start_h=0, end_h=23
            )
        )
        await callback.answer()

    elif current_state == NotificationFSM.create_end_time.state:
        start_hour = data.get("notification_start_time_hour")
        start_minute = data.get("notification_start_time_minute")
        await callback.message.edit_reply_markup(
            reply_markup=time_page_kb(
                page=callback_data.page,
                per_page=9,
                step_min=30,
                start_h=start_hour,
                start_m=start_minute,
                end_h=23,
            )
        )
        await callback.answer()

    elif current_state == NotificationFSM.create_sending_interval_minutes.state:
        await callback.message.edit_reply_markup(
            reply_markup=sending_interval_page_kb(
                page=callback_data.page, per_page=9, step_min=5
            )
        )
        await callback.answer()


@router.callback_query(F.data == "timecancel")
async def cancel_time(callback: CallbackQuery):
    await callback.message.edit_text("Выбор времени отменён.")
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
