"""
Утилиты для работы с командами бота.

Содержит функции для установки меню команд в Telegram.
"""

from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot) -> None:
    """
    Устанавливает меню команд для бота.

    Создаёт меню команд, которое будет отображаться в интерфейсе Telegram
    при нажатии на кнопку меню или при вводе "/".
    """
    commands = [
        BotCommand(command="start", description="Restart bot (Выбрать нейросеть)"),
        BotCommand(command="chatgpt", description="ChatGPT mode (Режим ChatGPT)"),
        BotCommand(command="profile", description="Profile (Профиль)"),
        BotCommand(command="premium", description="Premium"),
        BotCommand(command="language", description="Language (Язык)"),
        BotCommand(command="help", description="Support & Help (Помощь)"),
    ]

    await bot.set_my_commands(commands)

