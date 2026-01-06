"""
Роутер для команды /profile.

Обрабатывает команду просмотра профиля пользователя.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.text import make_profile_message

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


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    """
    Обработчик команды /profile.

    Отправляет пользователю информацию о его профиле.
    """
    logger.info("Команда /profile от пользователя: %s", _format_user(message))
    await message.answer(make_profile_message(message.from_user))

