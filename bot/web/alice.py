"""Alice webhook that forwards dictated text to a Telegram chat."""

import hmac
import logging
import re

from aiogram import Bot
from aiohttp import web

logger = logging.getLogger(__name__)
CHAT_ID_PATTERN = re.compile(r"-?\d{1,20}")


def alice_reply(text: str, *, end_session: bool = False) -> dict:
    """Build an Alice protocol response.

    :param text: Phrase Alice should say to the user.
    :param end_session: Whether to end the voice session.
    :return: A protocol version 1.0 response object.
    """
    return {"response": {"text": text, "end_session": end_session}, "version": "1.0"}


def create_alice_app(bot: Bot, secret: str) -> web.Application:
    """Create an HTTP app for one secret protected Alice webhook.

    :param bot: Telegram bot used to send dictated messages.
    :param secret: Unpredictable URL segment configured in Yandex Dialogs.
    :return: Configured aiohttp application.
    """
    if len(secret) < 32:
        raise ValueError("ALICE_WEBHOOK_SECRET must contain at least 32 characters")

    async def handle(request: web.Request) -> web.Response:
        """Validate an Alice request and send its utterance to Telegram.

        :param request: Incoming aiohttp request.
        :return: Alice protocol JSON or a validation error.
        """
        if not hmac.compare_digest(request.match_info["secret"], secret):
            raise web.HTTPNotFound()
        raw_chat_id = request.match_info["chat_id"]
        if not CHAT_ID_PATTERN.fullmatch(raw_chat_id):
            raise web.HTTPBadRequest(text="Invalid chat ID")
        try:
            payload = await request.json()
        except (ValueError, TypeError) as exc:
            raise web.HTTPBadRequest(text="Invalid JSON") from exc
        if not isinstance(payload, dict) or payload.get("version") != "1.0":
            raise web.HTTPBadRequest(text="Invalid Alice request")
        session = payload.get("session")
        utterance = (
            payload.get("request", {}).get("original_utterance")
            if isinstance(payload.get("request"), dict)
            else None
        )
        if (
            not isinstance(session, dict)
            or not isinstance(session.get("new"), bool)
            or not isinstance(utterance, str)
        ):
            raise web.HTTPBadRequest(text="Invalid Alice request")
        message = utterance.strip()
        if message == "ping":
            return web.json_response(alice_reply("На связи."))
        if not message:
            prompt = (
                "Что записать?"
                if session["new"]
                else "Повторите, пожалуйста, что записать."
            )
            return web.json_response(alice_reply(prompt))
        if len(message) > 1024:
            return web.json_response(
                alice_reply("Слишком длинная запись. Скажите короче.")
            )
        try:
            await bot.send_message(chat_id=int(raw_chat_id), text=message)
        except Exception:
            logger.exception(
                "Could not deliver Alice message to Telegram chat %s", raw_chat_id
            )
            return web.json_response(
                alice_reply("Не удалось записать. Повторите, пожалуйста.")
            )
        return web.json_response(alice_reply("Записала. Что ещё?"))

    app = web.Application(client_max_size=16 * 1024)
    app.router.add_post("/alice/{secret}/{chat_id}", handle)
    return app
