from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import KeyboardButton


def build_share_contact_markup() -> ReplyKeyboardMarkup:
    """Builder for share contact keyboard."""

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=("Share contact 📱"), request_contact=True),
            ],
        ],
        resize_keyboard=True,
    )