"""
Модуль конфигурации бота.

Отвечает за загрузку переменных окружения и предоставление настроек
остальным частям приложения.
"""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass
class BotConfig:
    """Конфигурация Telegram-бота."""

    bot_token: str


def load_config() -> BotConfig:
    """
    Загружает конфигурацию приложения из переменных окружения.

    Ожидается, что токен бота лежит в переменной TELEGRAM_BOT_TOKEN.
    """
    # Загружаем переменные окружения из файла .env (если он есть)
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден токен бота. "
            "Создайте файл .env и добавьте в него строку "
            "TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН"
        )

    return BotConfig(bot_token=token)


