"""
Тесты для сервиса работы с LLM (OpenRouter).
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.bot.services.llm import get_llm_response, DEFAULT_MODEL


@pytest.mark.asyncio
async def test_get_llm_response_success() -> None:
    """Тест успешного получения ответа от LLM."""
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Привет!"}]

    # Мокаем ответ от OpenRouter API
    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": "Привет! Как дела?",
                }
            }
        ]
    }

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_post
        )

        result = await get_llm_response(api_key, messages)

        assert result == "Привет! Как дела?"


@pytest.mark.asyncio
async def test_get_llm_response_uses_default_model() -> None:
    """Тест, что используется модель по умолчанию, если не указана."""
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    mock_response_data = {
        "choices": [{"message": {"content": "Ответ"}}]
    }

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_post
        )

        await get_llm_response(api_key, messages)

        # Проверяем, что в запросе использована модель по умолчанию
        call_args = mock_session.return_value.__aenter__.return_value.post.call_args
        assert call_args is not None
        payload = call_args[1]["json"]
        assert payload["model"] == DEFAULT_MODEL


@pytest.mark.asyncio
async def test_get_llm_response_custom_model() -> None:
    """Тест использования кастомной модели."""
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]
    custom_model = "openai/gpt-4"

    mock_response_data = {
        "choices": [{"message": {"content": "Ответ"}}]
    }

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_post
        )

        await get_llm_response(api_key, messages, model=custom_model)

        # Проверяем, что в запросе использована кастомная модель
        call_args = mock_session.return_value.__aenter__.return_value.post.call_args
        assert call_args is not None
        payload = call_args[1]["json"]
        assert payload["model"] == custom_model


@pytest.mark.asyncio
async def test_get_llm_response_api_error() -> None:
    """Тест обработки ошибки API (не 200 статус)."""
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")

        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_post
        )

        with pytest.raises(ValueError, match="OpenRouter API вернул ошибку 401"):
            await get_llm_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_invalid_format() -> None:
    """Тест обработки неожиданного формата ответа."""
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    # Ответ без поля "choices"
    mock_response_data = {"error": "Something went wrong"}

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_post
        )

        with pytest.raises(ValueError, match="Неожиданный формат ответа"):
            await get_llm_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_strips_whitespace() -> None:
    """Тест, что пробелы в начале и конце ответа обрезаются."""
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": "   Ответ с пробелами   ",
                }
            }
        ]
    }

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        mock_post = AsyncMock()
        mock_post.__aenter__ = AsyncMock(return_value=mock_response)
        mock_post.__aexit__ = AsyncMock(return_value=None)

        mock_session.return_value.__aenter__ = AsyncMock()
        mock_session.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_post
        )

        result = await get_llm_response(api_key, messages)

        assert result == "Ответ с пробелами"

