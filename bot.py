import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


# Настройка логирования: вывод в консоль и запись в файл в папке logs
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = LOGS_DIR / "bot.log"

logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Обработчик для записи логов в файл
file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
file_handler.setFormatter(formatter)

# Обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def load_config() -> str:
    """
    Загружает переменные окружения из .env и возвращает токен бота.
    Ожидает, что в файле .env есть переменная TELEGRAM_BOT_TOKEN.
    """
    # Загружаем переменные окружения из файла .env
    load_dotenv()

    # Получаем токен бота из переменных окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден токен бота. "
            "Создайте файл .env и добавьте в него строку TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН"
        )
    logger.info("Конфигурация загружена, токен бота получен из .env.")
    return token


def format_user(message: Message) -> str:
    """
    Вспомогательная функция для формирования строки с информацией о пользователе.
    Используется только для логирования.
    """
    user = message.from_user
    if user is None:
        return "неизвестный пользователь"

    username = f"@{user.username}" if user.username else "без username"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return f"id={user.id}, {username}, имя='{full_name}'"


async def start_handler(message: Message) -> None:
    """
    Обработчик команды /start.
    Отправляет пользователю приветственное сообщение.
    """
    # Логируем команду /start с информацией о пользователе
    logger.info("Команда /start от пользователя: %s", format_user(message))
    await message.answer(
        "Привет! Я простой эхо-бот.\n"
        "Напиши мне любое сообщение, и я повторю его обратно."
    )


async def echo_handler(message: Message) -> None:
    """
    Эхо-обработчик.
    Повторяет любое полученное текстовое сообщение и логирует его.
    """
    # Логируем текст входящего сообщения
    logger.info(
        "Получено сообщение от пользователя %s: %r",
        format_user(message),
        message.text,
    )

    # Отвечаем тем же текстом, который прислал пользователь
    await message.answer(message.text)


async def main() -> None:
    """
    Основная асинхронная функция.
    Настраивает бота, регистрирует хендлеры и запускает пуллинг.
    """
    # Загружаем токен бота из .env
    token = load_config()

    # Создаём экземпляры бота и диспетчера
    bot = Bot(token=token)
    dp = Dispatcher()

    # Регистрируем обработчик команды /start
    dp.message.register(start_handler, CommandStart())

    # Регистрируем эхо-обработчик на любые текстовые сообщения
    dp.message.register(echo_handler)

    logger.info("Бот запущен. Ожидаем сообщения...")

    # Запускаем бесконечный опрос сервера Telegram (long polling)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем асинхронную функцию main
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен пользователем.")