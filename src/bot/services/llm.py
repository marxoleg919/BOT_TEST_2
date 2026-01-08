"""
Сервис для работы с LLM через OpenRouter API.

Здесь нет зависимостей от aiogram и Telegram API.
"""

from typing import Any

import aiohttp


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Бесплатная модель Mistral 7B Instruct
# Суффикс :free указывает на бесплатный вариант модели
# Лимиты: 20 запросов/день без кредитов, 200 запросов/день с кредитами $5+
# Список бесплатных моделей: https://openrouter.ai/models?max_price=0
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"


class RateLimitError(Exception):
    """Исключение при превышении лимита запросов (429)."""

    pass


class ModelNotFoundError(Exception):
    """Исключение, когда модель не найдена (404)."""

    pass


async def get_llm_response(
    api_key: str,
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Отправляет запрос к LLM через OpenRouter API и возвращает ответ.

    Args:
        api_key: API ключ OpenRouter
        messages: Список сообщений в формате [{"role": "user", "content": "текст"}, ...]
        model: Идентификатор модели (по умолчанию gpt-4o-mini)

    Returns:
        Текст ответа от LLM

    Raises:
        aiohttp.ClientError: При ошибках сети
        ValueError: При некорректном ответе API
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",  # Опционально, для аналитики
    }

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_API_URL, headers=headers, json=payload) as response:
            if response.status == 429:
                raise RateLimitError(
                    "Превышен лимит запросов. Бесплатные модели имеют ограничения. "
                    "Попробуйте позже или используйте платную модель."
                )

            if response.status == 404:
                raise ModelNotFoundError(
                    f"Модель {model} не найдена. "
                    "Проверьте список доступных моделей: https://openrouter.ai/models"
                )

            if response.status != 200:
                error_text = await response.text()
                raise ValueError(
                    f"OpenRouter API вернул ошибку {response.status}: {error_text}"
                )

            data = await response.json()

            # Проверяем структуру ответа
            if "choices" not in data or not data["choices"]:
                raise ValueError(f"Неожиданный формат ответа от OpenRouter: {data}")

            # Извлекаем текст ответа
            choice = data["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise ValueError(f"Неожиданный формат ответа от OpenRouter: {data}")

            return choice["message"]["content"].strip()

