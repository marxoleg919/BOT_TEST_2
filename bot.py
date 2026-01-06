import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


# Включаем базовую конфигурацию логирования
# Логи можно будет сохранять в папку logs при необходимости
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
    return token


async def start_handler(message: Message) -> None:
    """
    Обработчик команды /start.
    Отправляет пользователю приветственное сообщение.
    """
    await message.answer(
        "Привет! Я простой эхо-бот.\n"
        "Напиши мне любое сообщение, и я повторю его обратно."
    )


async def echo_handler(message: Message) -> None:
    """
    Эхо-обработчик.
    Повторяет любое полученное текстовое сообщение.
    """
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