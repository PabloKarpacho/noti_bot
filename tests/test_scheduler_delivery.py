from datetime import UTC, datetime, time
from types import SimpleNamespace
import unittest

from bot.scheduler.delivery import get_due_templates, should_send_notification


def build_template(
    *,
    timezone: str = "UTC",
    time_start: time = time(hour=9, minute=0),
    interval: int = 15,
    time_stop: time | None = None,
    template_id: int = 1,
):
    return SimpleNamespace(
        notification_template_id=template_id,
        user=SimpleNamespace(timezone=timezone),
        time_start=time_start,
        time_stop=time_stop,
        sending_interval_minutes=interval,
    )


class ShouldSendNotificationTests(unittest.TestCase):
    def test_sends_when_time_matches_interval(self):
        template = build_template()

        result = should_send_notification(
            template,
            now_utc=datetime(2026, 3, 24, 9, 30, tzinfo=UTC),
        )

        self.assertTrue(result)

    def test_skips_before_start_time(self):
        template = build_template()

        result = should_send_notification(
            template,
            now_utc=datetime(2026, 3, 24, 8, 45, tzinfo=UTC),
        )

        self.assertFalse(result)

    def test_skips_when_not_on_interval(self):
        template = build_template(interval=20)

        result = should_send_notification(
            template,
            now_utc=datetime(2026, 3, 24, 9, 15, tzinfo=UTC),
        )

        self.assertFalse(result)

    def test_handles_overnight_window(self):
        template = build_template(
            timezone="Europe/Moscow",
            time_start=time(hour=23, minute=0),
            time_stop=time(hour=2, minute=0),
            interval=30,
        )

        result = should_send_notification(
            template,
            now_utc=datetime(2026, 3, 24, 22, 30, tzinfo=UTC),
        )

        self.assertTrue(result)

    def test_due_templates_filters_only_matching_ones(self):
        due_template = build_template(template_id=1)
        later_template = build_template(
            template_id=2,
            time_start=time(hour=10, minute=0),
            interval=30,
        )

        result = get_due_templates(
            [due_template, later_template],
            now_utc=datetime(2026, 3, 24, 9, 30, tzinfo=UTC),
        )

        self.assertEqual([template.notification_template_id for template in result], [1])


if __name__ == "__main__":
    unittest.main()
