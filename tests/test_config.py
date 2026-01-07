"""
Тесты для модуля конфигурации (`src.bot.config`).
"""

import os
from typing import Generator

import pytest

from src.bot.config import BotConfig, load_config


@pytest.fixture(autouse=True)
def clear_telegram_token_env() -> Generator[None, None, None]:
    """
    Фикстура очищает переменную TELEGRAM_BOT_TOKEN перед каждым тестом.

    Это помогает избежать влияния реального `.env` или окружения пользователя
    на результаты тестов.
    """
    old_value = os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    try:
        yield
    finally:
        # Восстанавливаем значение после теста, если оно было
        if old_value is not None:
            os.environ["TELEGRAM_BOT_TOKEN"] = old_value


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


