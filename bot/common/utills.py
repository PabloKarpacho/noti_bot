from typing import Optional, Union

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.inaccessible_message import InaccessibleMessage

from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import datetime


from bot.postgres.schema import User
from bot.postgres.crud import create_user, get_user_by_tg_id


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
        await state.clear()
        user = await create_user(user_tg_id=tg_id)

    return user


def tz_from_coords(lat: float, lon: float) -> str | None:
    tf = TimezoneFinder()
    return tf.timezone_at(lat=lat, lng=lon)
