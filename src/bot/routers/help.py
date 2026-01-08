"""
Роутер для команды /help.

Обрабатывает команду помощи и поддержки.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.text import make_help_message
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Обработчик команды /help.

    Отправляет пользователю информацию о помощи и поддержке.
    """
    logger.info("Команда /help от пользователя: %s", format_user_for_log(message))
    await message.answer(make_help_message())

