"""
Роутер с простым эхо-функционалом.

Содержит только обработчики Telegram-событий, бизнес-логика вынесена в services.
"""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.services.text import make_echo_reply, make_start_message

logger = logging.getLogger("bot")

router = Router()


def _format_user(message: Message) -> str:
    """
    Вспомогательная функция для формирования строки с информацией о пользователе.
    Используется только для логирования.
    """
    user = message.from_user
    if user is None:
        return "неизвестный пользователь"

    username = f"@{user.username}" if user.username else "без username"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return f"id={user.id}, {username}, имя='{full_name}'"


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.

    Отправляет пользователю приветственное сообщение и логирует команду.
    """
    logger.info("Команда /start от пользователя: %s", _format_user(message))
    await message.answer(make_start_message())


@router.message()
async def echo_message(message: Message) -> None:
    """
    Эхо-обработчик.

    Повторяет любое полученное текстовое сообщение и логирует его.
    """
    logger.info(
        "Получено сообщение от пользователя %s: %r",
        _format_user(message),
        message.text,
    )

    reply_text = make_echo_reply(message.text or "")
    await message.answer(reply_text)


