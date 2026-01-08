"""
Тесты для утилит работы с командами (`src.bot.utils.commands`).
"""

from typing import List

from aiogram.types import BotCommand

from src.bot.utils.commands import COMMANDS_SPEC, set_bot_commands


class DummyBot:
    """
    Поддельный бот для тестирования установки команд.

    Реальный `aiogram.Bot` здесь не нужен — достаточно объекта с методом
    `set_my_commands`, который сохраняет переданные команды.
    """

    def __init__(self) -> None:
        self.commands: List[BotCommand] = []

    async def set_my_commands(self, commands: List[BotCommand]) -> None:  # type: ignore[override]
        """Сохраняем команды, которые устанавливает утилита."""
        self.commands = commands


async def test_set_bot_commands_sets_expected_commands() -> None:
    """Утилита должна установить ожидаемый набор команд в бота."""
    bot = DummyBot()

    await set_bot_commands(bot)  # type: ignore[arg-type]

    # Проверяем, что команды были установлены
    assert bot.commands, "Список команд не должен быть пустым"

    commands_by_name = {cmd.command: cmd.description for cmd in bot.commands}

    # Ожидаемый набор команд из утилиты
    expected_commands = {
        "start": "Restart bot (Выбрать нейросеть)",
        "chatgpt": "ChatGPT mode (Режим ChatGPT)",
        "stop": "Stop ChatGPT mode (Выйти из режима ChatGPT)",
        "profile": "Profile (Профиль)",
        "premium": "Premium",
        "language": "Language (Язык)",
        "help": "Support & Help (Помощь)",
    }

    assert commands_by_name == expected_commands

    # Проверяем отсутствие дубликатов в спецификации
    names = [spec.name for spec in COMMANDS_SPEC]
    assert len(names) == len(set(names))


