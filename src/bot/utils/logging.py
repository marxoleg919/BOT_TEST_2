"""
Настройка логирования для Telegram-бота.

Выводит логи в консоль и записывает их в файл в папке logs.
"""

import logging
from pathlib import Path


def setup_logging() -> logging.Logger:
    """
    Создаёт и настраивает логгер для приложения.

    Возвращает основной логгер, которым можно пользоваться во всём проекте.
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    log_file_path = logs_dir / "bot.log"

    logger = logging.getLogger("bot")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Обработчик для записи логов в файл
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


