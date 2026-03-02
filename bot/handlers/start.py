from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.common.utills import auth_user
from bot.common.logging import get_logger
from bot.enums.stickers import StickersEnum

logger = get_logger()

router = Router()


@router.message(Command(commands=["start"]))
async def handle_start(
    message: Message,
    state: FSMContext,
) -> None:
    logger.info("Received /start from user_tg_id={}", message.from_user.id)

    await state.clear()

    tg_id = str(message.from_user.id)

    user = await auth_user(
        message=message,
        tg_id=tg_id,
        state=state,
    )

    if user:
        logger.info("Authorized user_tg_id={}, sending welcome", tg_id)

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
