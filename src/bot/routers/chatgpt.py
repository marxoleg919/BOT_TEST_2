"""
Роутер для команды /chatgpt.

Обрабатывает команду запуска ChatGPT-режима и текстовые сообщения в этом режиме.
"""

import asyncio
import logging
from contextlib import suppress

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.config import BotConfig
from src.bot.services.history import ChatHistoryRepository
from src.bot.services.llm import (
    LLMClient,
    LLMTimeoutError,
    ModelNotFoundError,
    RateLimitError,
    UpstreamError,
)
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("chatgpt"))
async def cmd_chatgpt(
    message: Message, history_repo: ChatHistoryRepository
) -> None:
    """
    Обработчик команды /chatgpt.

    Запускает режим ChatGPT для пользователя.
    """
    user = message.from_user
    if user is None:
        await message.answer("❌ Не удалось определить пользователя.")
        return

    logger.info("Команда /chatgpt от пользователя: %s", format_user_for_log(message))

    await history_repo.start_session(user.id)
    await message.answer(
        "🤖 Режим ChatGPT активирован!\n\n"
        "Теперь я буду отвечать как обычная LLM. "
        "Отправляйте мне сообщения, и я буду на них отвечать.\n\n"
        "Для выхода из режима используйте команду /stop."
    )


@router.message(Command("stop"))
async def cmd_stop(message: Message, history_repo: ChatHistoryRepository) -> None:
    """
    Обработчик команды /stop.

    Останавливает режим ChatGPT для пользователя.
    """
    user = message.from_user
    if user is None:
        await message.answer("❌ Не удалось определить пользователя.")
        return

    logger.info("Команда /stop от пользователя: %s", format_user_for_log(message))

    if await history_repo.is_active(user.id):
        await history_repo.stop_session(user.id)
        await message.answer("✅ Режим ChatGPT деактивирован.")
    else:
        await message.answer("ℹ️ Вы не находитесь в режиме ChatGPT.")


@router.message()
async def handle_chat_message(
    message: Message,
    config: BotConfig,
    history_repo: ChatHistoryRepository,
    llm_client: LLMClient,
) -> None:
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
    if not await history_repo.is_active(user.id):
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

    bot = message.bot
    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(
        _typing_loop(bot=bot, chat_id=message.chat.id, stop_event=stop_typing)
    )

    try:
        # Проверяем наличие API ключа
        if not config.openrouter_api_key:
            await message.answer(
                "❌ Ошибка: API ключ OpenRouter не настроен. "
                "Обратитесь к администратору."
            )
            logger.error("OpenRouter API ключ не найден для пользователя %s", user.id)
            return

        # Добавляем сообщение пользователя в историю
        await history_repo.add_user_message(user.id, user_text)

        # Получаем историю диалога
        history = await history_repo.get_history(user.id)

        # Отправляем запрос к LLM с моделью из конфигурации
        response_text = await llm_client.get_response(
            api_key=config.openrouter_api_key,
            messages=history,
            model=config.llm_model,
        )

        # Добавляем ответ в историю
        await history_repo.add_assistant_message(user.id, response_text)

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

    except LLMTimeoutError as e:
        logger.warning("Таймаут LLM для пользователя %s: %s", user.id, e)
        await message.answer(
            "⏳ Превышено время ожидания ответа модели. "
            "Попробуйте ещё раз или выйдите из режима /stop."
        )
    except UpstreamError as e:
        logger.error("Upstream ошибка для пользователя %s: %s", user.id, e)
        await message.answer(
            "❌ Провайдер временно недоступен. "
            "Попробуйте позже или используйте /stop для выхода из режима."
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

    finally:
        stop_typing.set()
        typing_task.cancel()
        with suppress(asyncio.CancelledError):
            await typing_task


async def _typing_loop(bot, chat_id: int, stop_event: asyncio.Event, interval: float = 4.0) -> None:
    """
    Отправляет action "typing" пока не будет остановлен stop_event.

    Telegram показывает статус ~5 секунд, поэтому повторяем каждые 4 секунды,
    пока обрабатываем запрос к LLM.
    """
    try:
        while not stop_event.is_set():
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue
    except Exception:
        # Не падаем из-за ошибок отправки "typing"
        return

