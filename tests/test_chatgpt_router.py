"""
Тесты для роутера ChatGPT.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import Message, User, Chat

from src.bot.config import BotConfig
from src.bot.routers.chatgpt import (
    _is_in_chat_mode,
    _start_chat_mode,
    _stop_chat_mode,
    _add_user_message,
    _add_assistant_message,
)


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


def test_chat_mode_management() -> None:
    """Тест управления режимом чата."""
    user_id = 123

    # Изначально пользователь не в режиме чата
    assert not _is_in_chat_mode(user_id)

    # Запускаем режим чата
    _start_chat_mode(user_id)
    assert _is_in_chat_mode(user_id)

    # Останавливаем режим чата
    _stop_chat_mode(user_id)
    assert not _is_in_chat_mode(user_id)


def test_chat_history_management() -> None:
    """Тест управления историей чата."""
    user_id = 123

    # Очищаем историю перед тестом
    _stop_chat_mode(user_id)

    # Добавляем сообщение пользователя
    _add_user_message(user_id, "Привет")
    assert _is_in_chat_mode(user_id)

    # Добавляем ответ ассистента
    _add_assistant_message(user_id, "Привет! Как дела?")

    # Проверяем, что история содержит оба сообщения
    from src.bot.routers.chatgpt import _chat_histories

    history = _chat_histories[user_id]
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Привет"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Привет! Как дела?"

    # Очищаем после теста
    _stop_chat_mode(user_id)


@pytest.mark.asyncio
async def test_cmd_chatgpt_activates_mode() -> None:
    """Тест команды /chatgpt - активация режима."""
    from src.bot.routers.chatgpt import cmd_chatgpt

    message = create_mock_message("/chatgpt")
    user_id = message.from_user.id if message.from_user else 0

    # Очищаем режим перед тестом
    _stop_chat_mode(user_id)

    await cmd_chatgpt(message)

    # Проверяем, что режим активирован
    assert _is_in_chat_mode(user_id)

    # Проверяем, что отправлено сообщение
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "Режим ChatGPT активирован" in call_args

    # Очищаем после теста
    _stop_chat_mode(user_id)


@pytest.mark.asyncio
async def test_cmd_stop_deactivates_mode() -> None:
    """Тест команды /stop - деактивация режима."""
    from src.bot.routers.chatgpt import cmd_stop

    message = create_mock_message("/stop")
    user_id = message.from_user.id if message.from_user else 0

    # Активируем режим перед тестом
    _start_chat_mode(user_id)

    await cmd_stop(message)

    # Проверяем, что режим деактивирован
    assert not _is_in_chat_mode(user_id)

    # Проверяем, что отправлено сообщение
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "деактивирован" in call_args


@pytest.mark.asyncio
async def test_cmd_stop_when_not_in_mode() -> None:
    """Тест команды /stop, когда пользователь не в режиме."""
    from src.bot.routers.chatgpt import cmd_stop

    message = create_mock_message("/stop")
    user_id = message.from_user.id if message.from_user else 0

    # Убеждаемся, что режим не активирован
    _stop_chat_mode(user_id)

    await cmd_stop(message)

    # Проверяем, что отправлено информационное сообщение
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "не находитесь в режиме" in call_args


@pytest.mark.asyncio
async def test_handle_chat_message_ignores_when_not_in_mode() -> None:
    """Тест, что обработчик игнорирует сообщения вне режима ChatGPT."""
    from src.bot.routers.chatgpt import handle_chat_message

    message = create_mock_message("Обычное сообщение")
    config = create_mock_config()
    user_id = message.from_user.id if message.from_user else 0

    # Убеждаемся, что режим не активирован
    _stop_chat_mode(user_id)

    await handle_chat_message(message, config)

    # Проверяем, что сообщение не обработано
    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_handle_chat_message_processes_in_mode() -> None:
    """Тест обработки сообщения в режиме ChatGPT."""
    from src.bot.routers.chatgpt import handle_chat_message

    message = create_mock_message("Привет, как дела?")
    config = create_mock_config()
    user_id = message.from_user.id if message.from_user else 0

    # Активируем режим
    _start_chat_mode(user_id)

    # Мокаем ответ от LLM
    mock_llm_response = "Привет! У меня всё отлично, спасибо!"

    with patch("src.bot.routers.chatgpt.get_llm_response") as mock_get_llm:
        mock_get_llm.return_value = mock_llm_response

        await handle_chat_message(message, config)

        # Проверяем, что отправлен запрос к LLM
        mock_get_llm.assert_called_once()

        # Проверяем, что отправлен ответ пользователю
        message.answer.assert_called_once_with(mock_llm_response)

        # Проверяем, что отправлено действие "печатает..." хотя бы один раз
        assert message.bot.send_chat_action.await_count >= 1

    # Очищаем после теста
    _stop_chat_mode(user_id)


@pytest.mark.asyncio
async def test_handle_chat_message_no_api_key() -> None:
    """Тест обработки сообщения без API ключа."""
    from src.bot.routers.chatgpt import handle_chat_message

    message = create_mock_message("Привет")
    config = create_mock_config(api_key=None)  # Без API ключа
    user_id = message.from_user.id if message.from_user else 0

    # Активируем режим
    _start_chat_mode(user_id)

    await handle_chat_message(message, config)

    # Проверяем, что отправлено сообщение об ошибке
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "API ключ OpenRouter не настроен" in call_args

    # Очищаем после теста
    _stop_chat_mode(user_id)


@pytest.mark.asyncio
async def test_handle_chat_message_ignores_commands() -> None:
    """Тест, что обработчик игнорирует команды."""
    from src.bot.routers.chatgpt import handle_chat_message

    message = create_mock_message("/start")
    config = create_mock_config()
    user_id = message.from_user.id if message.from_user else 0

    # Активируем режим
    _start_chat_mode(user_id)

    await handle_chat_message(message, config)

    # Проверяем, что сообщение не обработано (команды обрабатываются другими роутерами)
    message.answer.assert_not_called()

    # Очищаем после теста
    _stop_chat_mode(user_id)


@pytest.mark.asyncio
async def test_handle_chat_message_empty_text() -> None:
    """Тест обработки пустого сообщения."""
    from src.bot.routers.chatgpt import handle_chat_message

    message = create_mock_message("")
    config = create_mock_config()
    user_id = message.from_user.id if message.from_user else 0

    # Активируем режим
    _start_chat_mode(user_id)

    await handle_chat_message(message, config)

    # Проверяем, что отправлено сообщение с просьбой отправить текст
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "текстовое сообщение" in call_args

    # Очищаем после теста
    _stop_chat_mode(user_id)

