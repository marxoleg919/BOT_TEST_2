"""
Роутер для команды /language.

Обрабатывает команду для изменения языка интерфейса.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.text import make_language_message
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    """
    Обработчик команды /language.

    Отправляет пользователю меню выбора языка.
    """
    logger.info("Команда /language от пользователя: %s", format_user_for_log(message))
    await message.answer(make_language_message())

