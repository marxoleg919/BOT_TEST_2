"""
Сервис для работы с LLM через OpenRouter API.

Добавляет поддержку таймаутов, ретраев и переиспользования HTTP-сессии.
"""

from __future__ import annotations

import asyncio
import random
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

# Бесплатная модель Mistral 7B Instruct
# Суффикс :free указывает на бесплатный вариант модели
# Лимиты: 20 запросов/день без кредитов, 200 запросов/день с кредитами $5+
# Список бесплатных моделей: https://openrouter.ai/models?max_price=0
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"
DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class RateLimitError(Exception):
    """Исключение при превышении лимита запросов (429)."""


class ModelNotFoundError(Exception):
    """Исключение, когда модель не найдена (404)."""


class LLMTimeoutError(Exception):
    """Исключение при таймауте запроса к провайдеру."""


class UpstreamError(Exception):
    """Исключение при сетевых ошибках или 5xx ответах провайдера."""


class LLMClient:
    """Клиент OpenRouter с управлением сессией, таймаутами и ретраями."""

    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        referer: str | None = None,
        timeout_seconds: float = 20.0,
        retries: int = 3,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._api_url = api_url
        self._referer = referer
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._own_session = session is None
        self._session = session or aiohttp.ClientSession(
            timeout=ClientTimeout(total=timeout_seconds)
        )

    async def aclose(self) -> None:
        """Корректно закрывает HTTP-сессию, если клиент ей владеет."""
        if self._own_session and not self._session.closed:
            await self._session.close()

    async def get_response(
        self,
        api_key: str,
        messages: list[dict[str, str]],
        model: str = DEFAULT_MODEL,
    ) -> str:
        """Отправляет запрос к LLM и возвращает текст ответа."""
        attempt = 0
        last_error: Exception | None = None

        while attempt <= self._retries:
            try:
                return await self._send(api_key=api_key, messages=messages, model=model)
            except RateLimitError:
                raise
            except ModelNotFoundError:
                raise
            except asyncio.TimeoutError as exc:
                last_error = LLMTimeoutError("Таймаут запроса к LLM")
            except aiohttp.ClientError as exc:
                last_error = UpstreamError(f"Сетевая ошибка: {exc}")
            except UpstreamError as exc:
                last_error = exc

            attempt += 1
            if attempt > self._retries:
                break
            # Экспоненциальный бэкофф с джиттером
            delay = self._backoff(attempt)
            await asyncio.sleep(delay)

        assert last_error is not None
        raise last_error

    async def _send(
        self,
        api_key: str,
        messages: list[dict[str, str]],
        model: str,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if self._referer:
            headers["HTTP-Referer"] = self._referer

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }

        async with self._session.post(
            self._api_url,
            headers=headers,
            json=payload,
        ) as response:
            status = response.status

            if status == 429:
                raise RateLimitError(
                    "Превышен лимит запросов. Бесплатные модели имеют ограничения. "
                    "Попробуйте позже или используйте платную модель."
                )

            if status == 404:
                raise ModelNotFoundError(
                    f"Модель {model} не найдена. "
                    "Проверьте список доступных моделей: https://openrouter.ai/models"
                )

            if status in {500, 502, 503, 504}:
                error_text = await response.text()
                raise UpstreamError(f"Upstream ошибка {status}: {error_text}")

            if status != 200:
                error_text = await response.text()
                raise ValueError(
                    f"OpenRouter API вернул ошибку {status}: {error_text}"
                )

            data = await response.json()
            return self._parse_response(data)

    @staticmethod
    def _parse_response(data: dict[str, Any]) -> str:
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"Неожиданный формат ответа от OpenRouter: {data}")

        choice = data["choices"][0]
        if "message" not in choice or "content" not in choice["message"]:
            raise ValueError(f"Неожиданный формат ответа от OpenRouter: {data}")

        return str(choice["message"]["content"]).strip()

    @staticmethod
    def _backoff(attempt: int) -> float:
        base = 0.5 * (2 ** (attempt - 1))
        jitter = random.uniform(0, 0.25)
        return base + jitter

