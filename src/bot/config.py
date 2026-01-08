"""
Модуль конфигурации бота.

Отвечает за загрузку переменных окружения и предоставление настроек
остальным частям приложения.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Модель LLM по умолчанию для OpenRouter
DEFAULT_LLM_MODEL = "mistralai/mistral-7b-instruct:free"


@dataclass
class BotConfig:
    """Конфигурация Telegram-бота."""

    bot_token: str
    openrouter_api_key: str | None = None
    llm_model: str = DEFAULT_LLM_MODEL
    openrouter_api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    llm_timeout_sec: float = 20.0
    llm_retries: int = 3
    llm_referer: str | None = None

    chat_history_backend: str = "memory"  # memory | redis
    redis_url: str | None = None
    history_max_messages: int = 20
    history_ttl_sec: int = 60 * 60 * 24


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
    llm_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
    llm_timeout = float(os.getenv("LLM_TIMEOUT_SEC", "20"))
    llm_retries = int(os.getenv("LLM_RETRIES", "3"))
    openrouter_api_url = os.getenv(
        "OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"
    )
    llm_referer = os.getenv("LLM_REFERER")

    chat_history_backend = os.getenv("CHAT_HISTORY_BACKEND", "memory")
    redis_url = os.getenv("REDIS_URL")
    history_max_messages = int(os.getenv("HISTORY_MAX_MESSAGES", "20"))
    history_ttl_sec = int(os.getenv("HISTORY_TTL_SEC", str(60 * 60 * 24)))

    return BotConfig(
        bot_token=token,
        openrouter_api_key=openrouter_key,
        llm_model=llm_model,
        openrouter_api_url=openrouter_api_url,
        llm_timeout_sec=llm_timeout,
        llm_retries=llm_retries,
        llm_referer=llm_referer,
        chat_history_backend=chat_history_backend,
        redis_url=redis_url,
        history_max_messages=history_max_messages,
        history_ttl_sec=history_ttl_sec,
    )


