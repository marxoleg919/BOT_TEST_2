"""
Роутер для команды /language.

Обрабатывает команду для изменения языка интерфейса.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.text import make_language_message

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


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    """
    Обработчик команды /language.

    Отправляет пользователю меню выбора языка.
    """
    logger.info("Команда /language от пользователя: %s", _format_user(message))
    await message.answer(make_language_message())

