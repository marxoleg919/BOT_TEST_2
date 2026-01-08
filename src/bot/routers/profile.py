"""
Роутер для команды /profile.

Обрабатывает команду просмотра профиля пользователя.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.utils.formatting import format_user_for_log, format_user_profile

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    """
    Обработчик команды /profile.

    Отправляет пользователю информацию о его профиле.
    """
    logger.info("Команда /profile от пользователя: %s", format_user_for_log(message))
    await message.answer(format_user_profile(message.from_user))

