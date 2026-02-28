from aiogram.fsm.state import State, StatesGroup


class NotificationFSM(StatesGroup):
    """FSM for Notification"""

    create_name = State()
    """State when user is creating a notification name"""

    create_message = State()
    """State when user is creating a notification message"""

    create_start_time = State()
    """State when user is creating a notification start time"""

    create_end_time = State()
    """State when user is creating a notification end time"""

    create_sending_interval_minutes = State()
    """State when user is creating a notification sending interval in minutes"""

    create_timezone = State()
    """State when user is creating a notification timezone"""

    save_notification = State()
    """State when user is saving a notification"""

    delete_notification = State()
    """State when user is deleting a notification"""
