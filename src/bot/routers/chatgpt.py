"""
Роутер для команды /chatgpt.

Обрабатывает команду запуска ChatGPT-режима и текстовые сообщения в этом режиме.
"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.config import BotConfig
from src.bot.services.llm import ModelNotFoundError, RateLimitError, get_llm_response
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()

# Максимальное количество сообщений в истории диалога (пар user + assistant)
MAX_HISTORY_MESSAGES = 20

# Хранилище истории диалогов: user_id -> список сообщений
# Формат: [{"role": "user", "content": "текст"}, {"role": "assistant", "content": "ответ"}]
_chat_histories: dict[int, list[dict[str, str]]] = {}


def _is_in_chat_mode(user_id: int) -> bool:
    """Проверяет, находится ли пользователь в режиме ChatGPT."""
    return user_id in _chat_histories


def _start_chat_mode(user_id: int) -> None:
    """Начинает режим ChatGPT для пользователя."""
    _chat_histories[user_id] = []


def _stop_chat_mode(user_id: int) -> None:
    """Останавливает режим ChatGPT для пользователя."""
    _chat_histories.pop(user_id, None)


def _add_user_message(user_id: int, content: str) -> None:
    """Добавляет сообщение пользователя в историю."""
    if user_id not in _chat_histories:
        _start_chat_mode(user_id)
    _chat_histories[user_id].append({"role": "user", "content": content})
    _trim_history(user_id)


def _add_assistant_message(user_id: int, content: str) -> None:
    """Добавляет ответ ассистента в историю."""
    if user_id not in _chat_histories:
        _start_chat_mode(user_id)
    _chat_histories[user_id].append({"role": "assistant", "content": content})
    _trim_history(user_id)


def _trim_history(user_id: int) -> None:
    """Обрезает историю диалога до максимального размера."""
    if user_id not in _chat_histories:
        return
    history = _chat_histories[user_id]
    if len(history) > MAX_HISTORY_MESSAGES:
        # Удаляем старые сообщения, сохраняя последние MAX_HISTORY_MESSAGES
        _chat_histories[user_id] = history[-MAX_HISTORY_MESSAGES:]


@router.message(Command("chatgpt"))
async def cmd_chatgpt(message: Message) -> None:
    """
    Обработчик команды /chatgpt.

    Запускает режим ChatGPT для пользователя.
    """
    user = message.from_user
    if user is None:
        await message.answer("❌ Не удалось определить пользователя.")
        return

    logger.info("Команда /chatgpt от пользователя: %s", format_user_for_log(message))

    _start_chat_mode(user.id)
    await message.answer(
        "🤖 Режим ChatGPT активирован!\n\n"
        "Теперь я буду отвечать как обычная LLM. "
        "Отправляйте мне сообщения, и я буду на них отвечать.\n\n"
        "Для выхода из режима используйте команду /stop."
    )


@router.message(Command("stop"))
async def cmd_stop(message: Message) -> None:
    """
    Обработчик команды /stop.

    Останавливает режим ChatGPT для пользователя.
    """
    user = message.from_user
    if user is None:
        await message.answer("❌ Не удалось определить пользователя.")
        return

    logger.info("Команда /stop от пользователя: %s", format_user_for_log(message))

    if _is_in_chat_mode(user.id):
        _stop_chat_mode(user.id)
        await message.answer("✅ Режим ChatGPT деактивирован.")
    else:
        await message.answer("ℹ️ Вы не находитесь в режиме ChatGPT.")


@router.message()
async def handle_chat_message(message: Message, config: BotConfig) -> None:
    """
    Обработчик текстовых сообщений в режиме ChatGPT.

    Обрабатывает только сообщения от пользователей, которые находятся в режиме ChatGPT.

    Args:
        message: Сообщение от пользователя
        config: Конфигурация бота (передаётся через workflow_data)
    """
    user = message.from_user
    if user is None:
        return

    # Проверяем, что пользователь в режиме ChatGPT
    if not _is_in_chat_mode(user.id):
        return

    # Пропускаем команды (они обрабатываются другими роутерами)
    if message.text and message.text.startswith("/"):
        return

    user_text = message.text or ""
    if not user_text.strip():
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    logger.info(
        "Сообщение в режиме ChatGPT от пользователя %s: %r",
        format_user_for_log(message),
        user_text[:100],  # Логируем только первые 100 символов
    )

    try:
        # Отправляем действие "печатает..."
        bot = message.bot
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")

        # Проверяем наличие API ключа
        if not config.openrouter_api_key:
            await message.answer(
                "❌ Ошибка: API ключ OpenRouter не настроен. "
                "Обратитесь к администратору."
            )
            logger.error("OpenRouter API ключ не найден для пользователя %s", user.id)
            return

        # Добавляем сообщение пользователя в историю
        _add_user_message(user.id, user_text)

        # Получаем историю диалога
        history = _chat_histories[user.id].copy()

        # Отправляем запрос к LLM с моделью из конфигурации
        response_text = await get_llm_response(
            config.openrouter_api_key, history, model=config.llm_model
        )

        # Добавляем ответ в историю
        _add_assistant_message(user.id, response_text)

        # Отправляем ответ пользователю
        await message.answer(response_text)

    except RateLimitError as e:
        logger.warning(
            "Rate limit для пользователя %s: %s",
            user.id,
            e,
        )
        await message.answer(
            "⏳ Превышен лимит запросов к бесплатной модели.\n\n"
            "Бесплатные модели имеют ограничения:\n"
            "• 20 запросов/день без кредитов\n"
            "• 200 запросов/день с кредитами $5+\n\n"
            "Попробуйте позже или используйте команду /stop для выхода из режима."
        )

    except ModelNotFoundError as e:
        logger.error(
            "Модель не найдена для пользователя %s: %s",
            user.id,
            e,
        )
        await message.answer(
            "❌ Модель временно недоступна.\n\n"
            "Обратитесь к администратору для настройки другой модели."
        )

    except Exception as e:
        logger.error(
            "Ошибка при обработке сообщения в режиме ChatGPT: %s",
            e,
            exc_info=True,
        )
        await message.answer(
            "❌ Произошла ошибка при обработке запроса.\n\n"
            "Попробуйте позже или используйте команду /stop для выхода из режима."
        )

