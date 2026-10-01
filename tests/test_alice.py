"""Tests for the Alice voice-note webhook."""

import unittest
from unittest.mock import AsyncMock

from aiohttp.test_utils import TestClient, TestServer

from bot.web.alice import create_alice_app


class AliceWebhookTests(unittest.IsolatedAsyncioTestCase):
    """Check request validation and Telegram delivery."""

    async def asyncSetUp(self) -> None:
        """Start an isolated webhook with a mocked Telegram bot."""
        self.bot = AsyncMock()
        self.secret = "test-secret-with-32-characters-long"
        self.client = TestClient(TestServer(create_alice_app(self.bot, self.secret)))
        await self.client.start_server()

    async def asyncTearDown(self) -> None:
        """Close the HTTP test client."""
        await self.client.close()

    async def test_new_session_prompts_without_sending(self) -> None:
        """An empty invocation starts dictation without forwarding anything."""
        response = await self.client.post(
            f"/alice/{self.secret}/-123",
            json={
                "version": "1.0",
                "session": {"new": True},
                "request": {"type": "SimpleUtterance", "original_utterance": ""},
            },
        )
        self.assertEqual(response.status, 200)
        self.assertEqual((await response.json())["response"]["text"], "Что записать?")
        self.bot.send_message.assert_not_awaited()

    async def test_inline_utterance_is_sent(self) -> None:
        """A phrase supplied with skill activation is delivered immediately."""
        response = await self.client.post(
            f"/alice/{self.secret}/-123",
            json={
                "version": "1.0",
                "session": {"new": True},
                "request": {
                    "type": "SimpleUtterance",
                    "original_utterance": "Купить молоко",
                },
            },
        )
        self.assertEqual(
            (await response.json())["response"]["text"], "Записала. Что ещё?"
        )
        self.bot.send_message.assert_awaited_once_with(
            chat_id=-123, text="Купить молоко"
        )

    async def test_ping_does_not_send(self) -> None:
        """Yandex health checks must not appear as chat messages."""
        response = await self.client.post(
            f"/alice/{self.secret}/-123",
            json={
                "version": "1.0",
                "session": {"new": False},
                "request": {"type": "SimpleUtterance", "original_utterance": "ping"},
            },
        )
        self.assertEqual((await response.json())["response"]["text"], "На связи.")
        self.bot.send_message.assert_not_awaited()

    async def test_sends_dictated_text(self) -> None:
        """A subsequent utterance reaches the selected chat."""
        response = await self.client.post(
            f"/alice/{self.secret}/-123",
            json={
                "version": "1.0",
                "session": {"new": False},
                "request": {"original_utterance": "Купить молоко"},
            },
        )
        self.assertEqual(
            (await response.json())["response"]["text"], "Записала. Что ещё?"
        )
        self.bot.send_message.assert_awaited_once_with(
            chat_id=-123, text="Купить молоко"
        )

    async def test_wrong_secret_rejected(self) -> None:
        """An unknown URL secret cannot send messages."""
        response = await self.client.post("/alice/wrong/-123", json={})
        self.assertEqual(response.status, 404)
        self.bot.send_message.assert_not_awaited()

    async def test_invalid_request_rejected(self) -> None:
        """Malformed requests cannot be forwarded to Telegram."""
        response = await self.client.post(
            f"/alice/{self.secret}/-123",
            json={"request": {"original_utterance": ["bad"]}},
        )
        self.assertEqual(response.status, 400)
        self.bot.send_message.assert_not_awaited()

    async def test_telegram_failure_is_reported(self) -> None:
        """A failed Telegram call does not claim that a message was saved."""
        self.bot.send_message.side_effect = RuntimeError("telegram unavailable")
        response = await self.client.post(
            f"/alice/{self.secret}/-123",
            json={
                "version": "1.0",
                "session": {"new": False},
                "request": {"original_utterance": "Заметка"},
            },
        )
        self.assertEqual(
            (await response.json())["response"]["text"],
            "Не удалось записать. Повторите, пожалуйста.",
        )
