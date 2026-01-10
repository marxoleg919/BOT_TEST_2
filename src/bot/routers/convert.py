"""
Роутер для команды /convert.

Обрабатывает команду конвертации валют.
"""

import logging
import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.currency import (
    SUPPORTED_CURRENCIES,
    convert_currency,
    format_currency_result,
)
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


def parse_convert_command(text: str) -> tuple[float | None, str | None, str | None]:
    """
    Парсит команду конвертации валют.

    Поддерживаемые форматы:
    - /convert 100 USD EUR
    - /convert 100 USD to EUR
    - /convert 100 USD-EUR
    - /convert 100USD EUR
    - /convert 100 USDEUR

    Args:
        text: Текст команды с аргументами

    Returns:
        Кортеж (сумма, базовая валюта, целевая валюта) или (None, None, None) при ошибке
    """
    # Убираем команду /convert
    args_text = text.replace("/convert", "").strip()

    if not args_text:
        return None, None, None

    # Паттерн для поиска суммы (число с возможной точкой/запятой)
    # и двух кодов валют (3 заглавные буквы)
    pattern = r"(\d+(?:[.,]\d+)?)\s*([A-Z]{3})\s*(?:to|[-]|\s)?\s*([A-Z]{3})"
    match = re.search(pattern, args_text.upper())

    if not match:
        # Попробуем найти сумму и валюты отдельно
        # Ищем сумму в начале
        amount_match = re.search(r"(\d+(?:[.,]\d+)?)", args_text)
        # Ищем коды валют (3 заглавные буквы)
        currency_matches = re.findall(r"([A-Z]{3})", args_text.upper())

        if amount_match and len(currency_matches) >= 2:
            amount_str = amount_match.group(1).replace(",", ".")
            try:
                amount = float(amount_str)
                base_currency = currency_matches[0]
                target_currency = currency_matches[1]
                return amount, base_currency, target_currency
            except ValueError:
                return None, None, None

        return None, None, None

    amount_str = match.group(1).replace(",", ".")
    try:
        amount = float(amount_str)
        base_currency = match.group(2).upper()
        target_currency = match.group(3).upper()
        return amount, base_currency, target_currency
    except ValueError:
        return None, None, None


@router.message(Command("convert"))
async def cmd_convert(message: Message) -> None:
    """
    Обработчик команды /convert.

    Конвертирует сумму из одной валюты в другую.
    Формат: /convert <сумма> <базовая валюта> <целевая валюта>
    Пример: /convert 100 USD EUR
    """
    logger.info("Команда /convert от пользователя: %s", format_user_for_log(message))

    # Получаем полный текст сообщения
    command_text = message.text or ""

    # Парсим аргументы команды
    amount, base_currency, target_currency = parse_convert_command(command_text)

    # Проверяем, что все аргументы распознаны
    if amount is None or base_currency is None or target_currency is None:
        # Определяем, была ли команда вызвана просто без аргументов или с неправильными аргументами
        args_text = command_text.replace("/convert", "").strip()
        is_empty = not args_text
        
        currencies_list = ", ".join(SUPPORTED_CURRENCIES.keys())
        
        if is_empty:
            # Команда вызвана без аргументов - показываем дружелюбное сообщение
            await message.answer(
                "💱 Конвертер валют\n\n"
                "Эта команда позволяет конвертировать суммы из одной валюты в другую.\n\n"
                "📝 Использование:\n"
                "/convert <сумма> <базовая валюта> <целевая валюта>\n\n"
                "📌 Примеры:\n"
                "• /convert 100 USD EUR\n"
                "• /convert 100 USD to EUR\n"
                "• /convert 1000 RUB USD\n"
                "• /convert 50.5 EUR GBP\n\n"
                f"💵 Поддерживаемые валюты:\n{currencies_list}\n\n"
                "💡 Подсказка: вы можете использовать слово 'to' между валютами или просто пробел."
            )
        else:
            # Команда вызвана с аргументами, но они не распознаны - показываем ошибку
            await message.answer(
                "❌ Неверный формат команды.\n\n"
                "📝 Использование:\n"
                "/convert <сумма> <базовая валюта> <целевая валюта>\n\n"
                "📌 Примеры:\n"
                "• /convert 100 USD EUR\n"
                "• /convert 100 USD to EUR\n"
                "• /convert 1000 RUB USD\n\n"
                f"💵 Поддерживаемые валюты: {currencies_list}"
            )
        return

    # Проверяем, что сумма положительная
    if amount <= 0:
        await message.answer("❌ Сумма должна быть положительным числом.")
        return

    # Проверяем, что валюты поддерживаются
    if base_currency not in SUPPORTED_CURRENCIES:
        await message.answer(
            f"❌ Неподдерживаемая базовая валюта: {base_currency}\n\n"
            f"Поддерживаемые валюты: {', '.join(SUPPORTED_CURRENCIES.keys())}"
        )
        return

    if target_currency not in SUPPORTED_CURRENCIES:
        await message.answer(
            f"❌ Неподдерживаемая целевая валюта: {target_currency}\n\n"
            f"Поддерживаемые валюты: {', '.join(SUPPORTED_CURRENCIES.keys())}"
        )
        return

    # Проверяем, что валюты разные
    if base_currency == target_currency:
        await message.answer(
            f"❌ Базовая и целевая валюты не могут быть одинаковыми: {base_currency}"
        )
        return

    # Отправляем сообщение о начале конвертации
    await message.answer("⏳ Получаю актуальный курс валют...")

    # Выполняем конвертацию
    converted_amount, rate = await convert_currency(
        amount, base_currency, target_currency
    )

    # Проверяем результат
    if converted_amount is None or rate is None:
        logger.error(
            "Ошибка конвертации валют: amount=%s, base=%s, target=%s",
            amount,
            base_currency,
            target_currency,
        )
        await message.answer(
            "❌ Не удалось получить курс валют. Попробуйте позже.\n\n"
            "Возможные причины:\n"
            "• Проблемы с подключением к серверу курсов валют\n"
            "• Временная недоступность API"
        )
        return

    # Форматируем и отправляем результат
    result_text = format_currency_result(
        amount, base_currency, converted_amount, target_currency, rate
    )
    await message.answer(result_text)
    logger.info(
        "Конвертация выполнена: %.2f %s -> %.2f %s (курс: %.4f)",
        amount,
        base_currency,
        converted_amount,
        target_currency,
        rate,
    )
