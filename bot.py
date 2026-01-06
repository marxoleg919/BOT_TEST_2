"""
Временная точка входа для запуска бота командой:

    python bot.py

Рекомендуемый способ запуска:

    python -m src.bot
"""

import asyncio

from src.bot.main import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен пользователем.")