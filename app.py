"""
Точка входа для деплоя на Amvera.

Этот файл используется платформой Amvera для запуска бота.
Он импортирует и запускает основную функцию из src.bot.main.
"""

import asyncio

from src.bot.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
    except Exception as e:
        print(f"Критическая ошибка при запуске бота: {e}")
        raise
