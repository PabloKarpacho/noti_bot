from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

if TYPE_CHECKING:
    from bot.postgres.schema import NotificationTemplate


def normalize_utc_now(now_utc: datetime | None = None) -> datetime:
    if now_utc is None:
        return datetime.now(UTC)

    if now_utc.tzinfo is None:
        return now_utc.replace(tzinfo=UTC)

    return now_utc.astimezone(UTC)


def should_send_notification(
    notification_template: NotificationTemplate,
    now_utc: datetime | None = None,
) -> bool:
    timezone_name = notification_template.user.timezone
    if not timezone_name:
        return False

    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return False

    interval = notification_template.sending_interval_minutes
    if not interval or interval <= 0:
        return False

    normalized_now_utc = normalize_utc_now(now_utc)
    now_dt = normalized_now_utc.astimezone(tz).replace(second=0, microsecond=0)
    today = now_dt.date()

    start_dt = datetime.combine(
        today, notification_template.time_start, tzinfo=tz
    ).replace(second=0, microsecond=0)

    if notification_template.time_stop is None:
        if now_dt < start_dt:
            return False

        minutes_from_start = int((now_dt - start_dt).total_seconds() // 60)
        return minutes_from_start % interval == 0

    stop_dt = datetime.combine(
        today, notification_template.time_stop, tzinfo=tz
    ).replace(second=0, microsecond=0)

    if stop_dt < start_dt:
        stop_dt += timedelta(days=1)
        if now_dt < start_dt:
            now_dt += timedelta(days=1)

    if not (start_dt <= now_dt <= stop_dt):
        return False

    minutes_from_start = int((now_dt - start_dt).total_seconds() // 60)
    return minutes_from_start % interval == 0


def get_due_templates(
    notification_templates: Iterable[NotificationTemplate],
    now_utc: datetime | None = None,
) -> list[NotificationTemplate]:
    normalized_now_utc = normalize_utc_now(now_utc)
    return [
        template
        for template in notification_templates
        if should_send_notification(template, now_utc=normalized_now_utc)
    ]
