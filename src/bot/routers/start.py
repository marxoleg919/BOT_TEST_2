"""
Роутер для команды /start.

Обрабатывает команду запуска бота с возможностью выбора нейросети.
"""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.services.text import make_start_message

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

    Отправляет пользователю приветственное сообщение с возможностью выбора нейросети.
    """
    logger.info("Команда /start от пользователя: %s", _format_user(message))
    await message.answer(make_start_message())

