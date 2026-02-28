from aiogram.fsm.state import State, StatesGroup


class RegisterFSM(StatesGroup):
    """FSM for user register"""

    share_contact = State()
    """State when user share contact"""
