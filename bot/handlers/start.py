from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.common.utills import auth_user
from bot.enums.stickers import StickersEnum

router = Router()


@router.message(Command(commands=["start"]))
async def handle_start(
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

        await message.answer_sticker(
            sticker=StickersEnum.KIND_RABBIT,
        )

        await message.answer(
            text=(
                "👋 <b>Hello!</b>\n\n"
                "🔔 I'm your personal notification bot.\n"
                "I’ll help you create reminders and deliver them at the right time ⏰\n\n"
                "📌 <b>Available commands:</b>\n"
                "• /new_notification — create a new notification\n"
                "• /delete_notification — remove an existing notification\n"
            ),
            parse_mode="HTML",
        )
