from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class SelectedTime(
    CallbackData,
    prefix="time_callback",  # type: ignore[call-arg]
):
    hour: int
    minute: int


class SelectedTime(CallbackData, prefix="time_callback"):  # type: ignore[call-arg]
    hour: int
    minute: int


class SelectedSendingInterval(CallbackData, prefix="sending_interval_callback"):  # type: ignore[call-arg]
    minutes: int


class TimePage(CallbackData, prefix="time_page"):  # type: ignore[call-arg]
    page: int


class MarkDone(CallbackData, prefix="mark_done"):  # type: ignore[call-arg]
    is_done: bool
    notification_id: str


class SaveNotification(CallbackData, prefix="save_notification"):  # type: ignore[call-arg]
    state: str = "save"


def build_times(
    step_min: int = 30, start_h: int = 0, start_m: int = 0, end_h: int = 23
) -> list[tuple[int, int]]:
    times: list[tuple[int, int]] = []
    for h in range(start_h, end_h + 1):
        for m in range(start_m, 60, step_min):
            times.append((h, m))
    return times


def time_page_kb(
    page: int,
    per_page: int = 24,
    step_min: int = 30,
    start_h: int = 0,
    start_m: int = 0,
    end_h: int = 23,
):
    times = build_times(
        step_min=step_min, start_h=start_h, start_m=start_m, end_h=end_h
    )
    total_pages = (len(times) + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))

    chunk = times[page * per_page : (page + 1) * per_page]

    kb = InlineKeyboardBuilder()

    # Кнопки времени
    for h, m in chunk:
        kb.button(
            text=f"{h:02d}:{m:02d}",
            callback_data=SelectedTime(hour=h, minute=m).pack(),
        )

    kb.adjust(4)

    # Навигация
    nav = InlineKeyboardBuilder()
    prev_page = (page - 1) % total_pages
    next_page = (page + 1) % total_pages

    nav.button(text="◀️", callback_data=TimePage(page=prev_page).pack())
    nav.button(text=f"{page + 1}/{total_pages}", callback_data="noop")
    nav.button(text="▶️", callback_data=TimePage(page=next_page).pack())
    nav.button(text="✖️ Отмена", callback_data="timecancel")
    nav.adjust(3, 1)

    kb.attach(nav)
    return kb.as_markup()


def sending_interval_page_kb(
    page: int,
    per_page: int = 24,
    step_min: int = 5,
):

    times = range(5, 60, step_min)
    total_pages = (len(times) + per_page - 1) // per_page
    page = max(0, min(page, total_pages - 1))

    chunk = times[page * per_page : (page + 1) * per_page]

    kb = InlineKeyboardBuilder()

    # Кнопки времени
    for m in chunk:
        kb.button(
            text=f"{m:02d}",
            callback_data=SelectedSendingInterval(minutes=m).pack(),
        )

    kb.adjust(4)

    # Навигация
    nav = InlineKeyboardBuilder()
    prev_page = (page - 1) % total_pages
    next_page = (page + 1) % total_pages

    nav.button(text="◀️", callback_data=TimePage(page=prev_page).pack())
    nav.button(text=f"{page + 1}/{total_pages}", callback_data="noop")
    nav.button(text="▶️", callback_data=TimePage(page=next_page).pack())
    nav.button(text="✖️ Отмена", callback_data="timecancel")
    nav.adjust(3, 1)

    kb.attach(nav)
    return kb.as_markup()


def mark_notification_as_done_kb(notification_id: str):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="✅",
        callback_data=MarkDone(is_done=True, notification_id=notification_id).pack(),
    )
    return kb.as_markup()


def build_save_notification_kb():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="💾 Save",
        callback_data=SaveNotification().pack(),
    )
    return kb.as_markup()
