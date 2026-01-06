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
from src.bot.utils.commands import set_bot_commands
from src.bot.utils.logging import setup_logging


async def main() -> None:
    """
    Основная асинхронная функция приложения.
    """
    logger = setup_logging()
    logger.info("Запуск Telegram-бота...")

    config = load_config()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # Подключаем корневой роутер со всеми обработчиками
    dp.include_router(get_main_router())

    # Устанавливаем меню команд бота
    try:
        await set_bot_commands(bot)
        logger.info("Меню команд успешно установлено")
    except Exception as e:
        logger.error("Ошибка при установке меню команд: %s", e, exc_info=True)

    logger.info("Бот запущен. Ожидаем сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Здесь логгер уже настроен внутри main, поэтому просто печатаем в консоль
        print("Бот остановлен пользователем.")


