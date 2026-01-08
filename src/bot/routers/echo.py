"""
Роутер с простым эхо-функционалом.

Содержит только обработчики Telegram-событий, бизнес-логика вынесена в services.
Обрабатывает только текстовые сообщения, которые не являются командами.
"""

import logging

from aiogram import Router
from aiogram.types import Message

from src.bot.services.text import make_echo_reply
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


@router.message()
async def echo_message(message: Message) -> None:
    """
    Эхо-обработчик.

    Повторяет любое полученное текстовое сообщение и логирует его.
    Обрабатывает только сообщения, которые не были обработаны другими роутерами.
    """
    logger.info(
        "Получено сообщение от пользователя %s: %r",
        format_user_for_log(message),
        message.text,
    )

    reply_text = make_echo_reply(message.text or "")
    await message.answer(reply_text)


