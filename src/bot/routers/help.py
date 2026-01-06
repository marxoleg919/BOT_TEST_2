"""
Роутер для команды /help.

Обрабатывает команду помощи и поддержки.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.text import make_help_message

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


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Обработчик команды /help.

    Отправляет пользователю информацию о помощи и поддержке.
    """
    logger.info("Команда /help от пользователя: %s", _format_user(message))
    await message.answer(make_help_message())

