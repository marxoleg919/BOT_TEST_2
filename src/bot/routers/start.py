"""
Роутер для команды /start.

Обрабатывает команду запуска бота с возможностью выбора нейросети.
"""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.services.text import make_start_message
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.

    Отправляет пользователю приветственное сообщение с возможностью выбора нейросети.
    """
    logger.info("Команда /start от пользователя: %s", format_user_for_log(message))
    await message.answer(make_start_message())

