"""
Тесты для роутера ChatGPT.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from src.bot.config import BotConfig
from src.bot.routers.chatgpt import cmd_chatgpt, cmd_stop, handle_chat_message
from src.bot.services.history import ChatHistoryRepository


class FakeHistoryRepo(ChatHistoryRepository):
    """Простое in-memory хранилище для тестов."""

    def __init__(self, max_messages: int = 20) -> None:
        self.data: dict[int, list[dict[str, str]]] = {}
        self.max_messages = max_messages

    async def start_session(self, user_id: int) -> None:
        self.data[user_id] = []

    async def stop_session(self, user_id: int) -> None:
        self.data.pop(user_id, None)

    async def is_active(self, user_id: int) -> bool:
        return user_id in self.data

    async def add_user_message(self, user_id: int, content: str) -> None:
        await self._ensure(user_id)
        self.data[user_id].append({"role": "user", "content": content})
        await self.trim(user_id)

    async def add_assistant_message(self, user_id: int, content: str) -> None:
        await self._ensure(user_id)
        self.data[user_id].append({"role": "assistant", "content": content})
        await self.trim(user_id)

    async def get_history(self, user_id: int) -> list[dict[str, str]]:
        return list(self.data.get(user_id, []))

    async def trim(self, user_id: int) -> None:
        if user_id not in self.data:
            return
        if len(self.data[user_id]) > self.max_messages:
            self.data[user_id] = self.data[user_id][-self.max_messages :]

    async def aclose(self) -> None:
        return

    async def _ensure(self, user_id: int) -> None:
        if user_id not in self.data:
            self.data[user_id] = []


class FakeLLMClient:
    """Фейковый LLM клиент для тестов."""

    def __init__(self, response: str = "ok") -> None:
        self.response = response
        self.calls: list[tuple[str, list[dict[str, str]], str]] = []

    async def get_response(
        self, api_key: str, messages: list[dict[str, str]], model: str
    ) -> str:
        self.calls.append((api_key, messages, model))
        return self.response


def create_mock_config(
    api_key: str | None = "test_api_key",
    llm_model: str = "test-model",
) -> BotConfig:
    """Создаёт мок-объект BotConfig для тестов."""
    return BotConfig(
        bot_token="test_bot_token",
        openrouter_api_key=api_key,
        llm_model=llm_model,
    )


def create_mock_message(text: str, user_id: int = 123) -> Message:
    """Создаёт мок-объект Message для тестов."""
    user = User(
        id=user_id,
        is_bot=False,
        first_name="Test",
        username="testuser",
    )
    chat = Chat(id=user_id, type="private")
    message = Message(
        message_id=1,
        date=None,
        chat=chat,
        from_user=user,
    )
    message.text = text
    message.answer = AsyncMock()
    message.bot = MagicMock()
    message.bot.send_chat_action = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_history_repository_basic() -> None:
    """Проверяем базовые операции репозитория истории."""
    repo = FakeHistoryRepo(max_messages=2)
    user_id = 1

    assert not await repo.is_active(user_id)
    await repo.start_session(user_id)
    assert await repo.is_active(user_id)

    await repo.add_user_message(user_id, "a")
    await repo.add_assistant_message(user_id, "b")
    history = await repo.get_history(user_id)
    assert len(history) == 2

    await repo.add_user_message(user_id, "c")
    history = await repo.get_history(user_id)
    # Лимит 2 сообщения => оставляем последние
    assert len(history) == 2
    assert history[-1]["content"] == "c"

    await repo.stop_session(user_id)
    assert not await repo.is_active(user_id)


@pytest.mark.asyncio
async def test_cmd_chatgpt_activates_mode() -> None:
    message = create_mock_message("/chatgpt")
    repo = FakeHistoryRepo()

    await cmd_chatgpt(message, repo)

    assert await repo.is_active(message.from_user.id)  # type: ignore[arg-type]
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_cmd_stop_deactivates_mode() -> None:
    message = create_mock_message("/stop")
    repo = FakeHistoryRepo()
    await repo.start_session(message.from_user.id)  # type: ignore[arg-type]

    await cmd_stop(message, repo)

    assert not await repo.is_active(message.from_user.id)  # type: ignore[arg-type]
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_cmd_stop_when_not_in_mode() -> None:
    message = create_mock_message("/stop")
    repo = FakeHistoryRepo()

    await cmd_stop(message, repo)

    message.answer.assert_called_once()
    assert "не находитесь" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_chat_message_ignores_when_not_in_mode() -> None:
    config = create_mock_config()
    message = create_mock_message("Обычное сообщение")
    repo = FakeHistoryRepo()
    llm_client = FakeLLMClient()

    await handle_chat_message(message, config, repo, llm_client)

    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_chat_message_processes_in_mode() -> None:
    config = create_mock_config()
    message = create_mock_message("Привет, как дела?")
    repo = FakeHistoryRepo()
    llm_client = FakeLLMClient("Привет! У меня всё отлично, спасибо!")
    await repo.start_session(message.from_user.id)  # type: ignore[arg-type]

    await handle_chat_message(message, config, repo, llm_client)

    assert message.answer.called
    assert llm_client.calls
    assert message.bot.send_chat_action.await_count >= 1


@pytest.mark.asyncio
async def test_handle_chat_message_no_api_key() -> None:
    config = create_mock_config(api_key=None)
    message = create_mock_message("Привет")
    repo = FakeHistoryRepo()
    llm_client = FakeLLMClient()
    await repo.start_session(message.from_user.id)  # type: ignore[arg-type]

    await handle_chat_message(message, config, repo, llm_client)

    message.answer.assert_called_once()
    assert "API ключ OpenRouter не настроен" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_chat_message_ignores_commands() -> None:
    config = create_mock_config()
    message = create_mock_message("/start")
    repo = FakeHistoryRepo()
    llm_client = FakeLLMClient()
    await repo.start_session(message.from_user.id)  # type: ignore[arg-type]

    await handle_chat_message(message, config, repo, llm_client)

    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_chat_message_empty_text() -> None:
    config = create_mock_config()
    message = create_mock_message("")
    repo = FakeHistoryRepo()
    llm_client = FakeLLMClient()
    await repo.start_session(message.from_user.id)  # type: ignore[arg-type]

    await handle_chat_message(message, config, repo, llm_client)

    message.answer.assert_called_once()
    assert "текстовое сообщение" in message.answer.call_args[0][0]

