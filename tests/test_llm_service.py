"""
Тесты для сервиса работы с LLM (OpenRouter).
"""

from typing import Any, List, Optional

import pytest

from src.bot.services.llm import (
    DEFAULT_MODEL,
    LLMClient,
    ModelNotFoundError,
    RateLimitError,
    UpstreamError,
)


class DummyResponse:
    """Поддельный ответ aiohttp."""

    def __init__(self, status: int, json_data: Optional[dict[str, Any]] = None, text: str = "") -> None:
        self.status = status
        self._json_data = json_data or {}
        self._text = text

    async def json(self) -> dict[str, Any]:
        return self._json_data

    async def text(self) -> str:
        return self._text

    async def __aenter__(self) -> "DummyResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class DummySession:
    """Поддельная HTTP-сессия для LLMClient."""

    def __init__(self, responses: List[DummyResponse]) -> None:
        self.responses = responses
        self.last_json: dict[str, Any] | None = None
        self.last_headers: dict[str, str] | None = None
        self.closed = False

    def post(self, url: str, headers: dict[str, str], json: dict[str, Any]):
        self.last_json = json
        self.last_headers = headers
        if not self.responses:
            raise RuntimeError("No responses left in DummySession")
        return self.responses.pop(0)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_get_llm_response_success() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Привет!"}]

    session = DummySession(
        [DummyResponse(status=200, json_data={"choices": [{"message": {"content": "Привет! Как дела?"}}]})]
    )
    client = LLMClient(session=session)

    result = await client.get_response(api_key, messages)

    assert result == "Привет! Как дела?"
    assert session.last_json is not None
    assert session.last_json["model"] == DEFAULT_MODEL


@pytest.mark.asyncio
async def test_get_llm_response_custom_model() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]
    custom_model = "openai/gpt-4"

    session = DummySession(
        [DummyResponse(status=200, json_data={"choices": [{"message": {"content": "Ответ"}}]})]
    )
    client = LLMClient(session=session)

    await client.get_response(api_key, messages, model=custom_model)

    assert session.last_json is not None
    assert session.last_json["model"] == custom_model


@pytest.mark.asyncio
async def test_get_llm_response_rate_limit_error() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    session = DummySession([DummyResponse(status=429, json_data={})])
    client = LLMClient(session=session, retries=0)

    with pytest.raises(RateLimitError):
        await client.get_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_model_not_found() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    session = DummySession([DummyResponse(status=404, json_data={})])
    client = LLMClient(session=session, retries=0)

    with pytest.raises(ModelNotFoundError):
        await client.get_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_upstream_error() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    session = DummySession([DummyResponse(status=503, json_data={}, text="Service Unavailable")])
    client = LLMClient(session=session, retries=0)

    with pytest.raises(UpstreamError):
        await client.get_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_api_error() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    session = DummySession([DummyResponse(status=401, json_data={}, text="Unauthorized")])
    client = LLMClient(session=session, retries=0)

    with pytest.raises(ValueError):
        await client.get_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_invalid_format() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    session = DummySession([DummyResponse(status=200, json_data={"error": "Something went wrong"})])
    client = LLMClient(session=session, retries=0)

    with pytest.raises(ValueError, match="Неожиданный формат ответа"):
        await client.get_response(api_key, messages)


@pytest.mark.asyncio
async def test_get_llm_response_strips_whitespace() -> None:
    api_key = "test_api_key"
    messages = [{"role": "user", "content": "Тест"}]

    session = DummySession(
        [
            DummyResponse(
                status=200,
                json_data={"choices": [{"message": {"content": "   Ответ с пробелами   "}}]},
            )
        ]
    )
    client = LLMClient(session=session, retries=0)

    result = await client.get_response(api_key, messages)

    assert result == "Ответ с пробелами"

