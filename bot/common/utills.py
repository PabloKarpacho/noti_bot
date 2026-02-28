from typing import Optional, Union

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.inaccessible_message import InaccessibleMessage

from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import datetime


from bot.postgres.schema import User
from bot.keyboards.share_contact import build_share_contact_markup
from bot.states.register import RegisterFSM
from bot.postgres.crud import get_user_by_tg_id


async def auth_user(
    message: Union[Message, InaccessibleMessage, None],
    tg_id: str,
    state: FSMContext,
) -> Optional[User]:
    """
    Try authorize in bot.

    :param message: Message from user.
    :param tg_id: Telegram user id.
    :param state: FSM state.
    """

    user = await get_user_by_tg_id(user_tg_id=tg_id)

    if not user:
        await state.set_state(RegisterFSM.share_contact)

        await message.answer(  # type: ignore[union-attr]
            text="Click the 'Share Contact' button\n" "to log in 👇",
            reply_markup=build_share_contact_markup(),
        )
        return None

    return user


def tz_from_coords(lat: float, lon: float) -> str | None:
    tf = TimezoneFinder()
    return tf.timezone_at(lat=lat, lng=lon)
