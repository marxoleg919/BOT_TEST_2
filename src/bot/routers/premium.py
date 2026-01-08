"""
Роутер для команды /premium.

Обрабатывает команду для работы с премиум-подпиской.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.text import make_premium_message
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("premium"))
async def cmd_premium(message: Message) -> None:
    """
    Обработчик команды /premium.

    Отправляет пользователю информацию о премиум-подписке.
    """
    logger.info("Команда /premium от пользователя: %s", format_user_for_log(message))
    await message.answer(make_premium_message())

