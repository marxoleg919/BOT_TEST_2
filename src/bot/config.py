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
    openrouter_api_key: str | None = None


def load_config() -> BotConfig:
    """
    Загружает конфигурацию приложения из переменных окружения.

    Ожидается, что токен бота лежит в переменной TELEGRAM_BOT_TOKEN.
    OPENROUTER_API_KEY опционален (нужен только для команды /chatgpt).
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

    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    return BotConfig(bot_token=token, openrouter_api_key=openrouter_key)


