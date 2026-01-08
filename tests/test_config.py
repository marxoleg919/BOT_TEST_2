"""
Тесты для модуля конфигурации (`src.bot.config`).
"""

import os
from typing import Generator

import pytest

from src.bot.config import BotConfig, load_config


@pytest.fixture(autouse=True)
def clear_env_vars() -> Generator[None, None, None]:
    """
    Фикстура очищает переменные окружения перед каждым тестом.

    Это помогает избежать влияния реального `.env` или окружения пользователя
    на результаты тестов.
    """
    old_token = os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    old_openrouter = os.environ.pop("OPENROUTER_API_KEY", None)
    try:
        yield
    finally:
        # Восстанавливаем значения после теста, если они были
        if old_token is not None:
            os.environ["TELEGRAM_BOT_TOKEN"] = old_token
        if old_openrouter is not None:
            os.environ["OPENROUTER_API_KEY"] = old_openrouter


def test_load_config_raises_when_token_missing() -> None:
    """Если TELEGRAM_BOT_TOKEN не установлен, должна быть поднята ошибка."""
    with pytest.raises(RuntimeError) as exc_info:
        load_config()

    assert "Не найден токен бота" in str(exc_info.value)


def test_load_config_returns_botconfig_when_token_present() -> None:
    """При наличии TELEGRAM_BOT_TOKEN должен возвращаться корректный BotConfig."""
    os.environ["TELEGRAM_BOT_TOKEN"] = "TEST_TOKEN"

    config = load_config()

    assert isinstance(config, BotConfig)
    assert config.bot_token == "TEST_TOKEN"
    assert config.openrouter_api_key is None


def test_load_config_includes_openrouter_key_when_present() -> None:
    """При наличии OPENROUTER_API_KEY он должен быть включён в конфигурацию."""
    os.environ["TELEGRAM_BOT_TOKEN"] = "TEST_TOKEN"
    os.environ["OPENROUTER_API_KEY"] = "TEST_OPENROUTER_KEY"

    config = load_config()

    assert config.bot_token == "TEST_TOKEN"
    assert config.openrouter_api_key == "TEST_OPENROUTER_KEY"


