from email import message

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from bot.common.logging import get_logger
from bot.postgres.crud import create_user, get_user_by_tg_id

logger = get_logger()

router = Router()


@router.message(F.contact)
async def handle_register(
    message: Message,
    bot: Bot,
    state: FSMContext,
) -> None:
    logger.info(
        "Received contact for registration from user_tg_id={}", message.from_user.id
    )

    await state.clear()

    tg_id = str(message.from_user.id)  # type: ignore[union-attr]

    user = await get_user_by_tg_id(user_tg_id=tg_id)
    if not user:
        logger.info("User not found, creating new user with tg_id={}", tg_id)

        await create_user(user_tg_id=tg_id)

        await message.answer(
            text=(
                "🎉 <b>Welcome aboard!</b>\n\n"
                "✅ Your account has been successfully activated.\n"
                "🙏 We truly appreciate your trust.\n\n"
                "🚀 Use command /start to continue."
            ),
            parse_mode="HTML",
        )
    else:
        logger.debug("User already registered: tg_id={}", tg_id)
