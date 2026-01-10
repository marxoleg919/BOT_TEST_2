"""
Утилиты для работы с командами бота.

Содержит единый список команд и установку меню.
"""

from dataclasses import dataclass
from typing import Iterable

from aiogram import Bot
from aiogram.types import BotCommand


@dataclass(frozen=True)
class CommandSpec:
    """Описание команды бота."""

    name: str
    description: str
    in_menu: bool = True


COMMANDS_SPEC: tuple[CommandSpec, ...] = (
    CommandSpec("start", "Restart bot (Выбрать нейросеть)"),
    CommandSpec("chatgpt", "ChatGPT mode (Режим ChatGPT)"),
    CommandSpec("stop", "Stop ChatGPT mode (Выйти из режима ChatGPT)", in_menu=True),
    CommandSpec("convert", "Currency converter (Конвертер валют)"),
    CommandSpec("profile", "Profile (Профиль)"),
    CommandSpec("premium", "Premium"),
    CommandSpec("language", "Language (Язык)"),
    CommandSpec("help", "Support & Help (Помощь)"),
)


def iter_menu_commands(specs: Iterable[CommandSpec]) -> list[BotCommand]:
    """Строит список команд для меню на основе спецификаций."""
    return [
        BotCommand(command=spec.name, description=spec.description)
        for spec in specs
        if spec.in_menu
    ]


async def set_bot_commands(bot: Bot) -> None:
    """Устанавливает меню команд для бота."""
    import logging
    
    logger = logging.getLogger("bot")
    commands = iter_menu_commands(COMMANDS_SPEC)
    
    # Логируем команды, которые будут установлены
    command_names = [cmd.command for cmd in commands]
    logger.info("Устанавливаем меню команд: %s", ", ".join(command_names))
    
    await bot.set_my_commands(commands)
    logger.info("Меню команд успешно установлено в Telegram")

