"""
Точка входа Telegram-бота.

Здесь выполняется:
- загрузка конфигурации;
- настройка логирования;
- инициализация aiogram-бота и диспетчера;
- регистрация роутеров;
- установка меню команд;
- запуск long polling.
"""

import asyncio

from aiogram import Bot, Dispatcher

from src.bot.config import load_config
from src.bot.routers import get_main_router
from src.bot.services.history import HistorySettings, build_history_repository
from src.bot.services.llm import LLMClient
from src.bot.utils.commands import set_bot_commands
from src.bot.utils.logging import setup_logging


async def main() -> None:
    """
    Основная асинхронная функция приложения.
    """
    logger = setup_logging()
    logger.info("Запуск Telegram-бота...")

    config = load_config()

    history_settings = HistorySettings(
        max_messages=config.history_max_messages,
        ttl_seconds=config.history_ttl_sec,
    )
    history_repo = build_history_repository(
        backend=config.chat_history_backend,
        settings=history_settings,
        redis_url=config.redis_url,
    )

    llm_client = LLMClient(
        api_url=config.openrouter_api_url,
        referer=config.llm_referer,
        timeout_seconds=config.llm_timeout_sec,
        retries=config.llm_retries,
    )

    bot = Bot(token=config.bot_token)
    # Передаём конфигурацию через workflow_data для доступа из роутеров
    dp = Dispatcher()
    dp["config"] = config
    dp["history_repo"] = history_repo
    dp["llm_client"] = llm_client

    # Подключаем корневой роутер со всеми обработчиками
    dp.include_router(get_main_router())

    # Устанавливаем меню команд бота
    try:
        await set_bot_commands(bot)
        logger.info("Меню команд успешно установлено")
    except Exception as e:
        logger.error("Ошибка при установке меню команд: %s", e, exc_info=True)

    logger.info("Бот запущен. Ожидаем сообщения...")
    try:
        await dp.start_polling(bot)
    finally:
        await llm_client.aclose()
        await history_repo.aclose()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Здесь логгер уже настроен внутри main, поэтому просто печатаем в консоль
        print("Бот остановлен пользователем.")


