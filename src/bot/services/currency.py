"""
Сервис конвертации валют.

Получает актуальные курсы валют и выполняет конвертацию.
Не зависит от aiogram и Telegram API.
"""

import logging
from typing import Any

import aiohttp

logger = logging.getLogger("bot")

# Список поддерживаемых валют
SUPPORTED_CURRENCIES = {
    "USD": "🇺🇸 Доллар США",
    "EUR": "🇪🇺 Евро",
    "RUB": "🇷🇺 Российский рубль",
    "GBP": "🇬🇧 Фунт стерлингов",
    "JPY": "🇯🇵 Японская йена",
    "CNY": "🇨🇳 Китайский юань",
    "CHF": "🇨🇭 Швейцарский франк",
    "AUD": "🇦🇺 Австралийский доллар",
    "CAD": "🇨🇦 Канадский доллар",
    "TRY": "🇹🇷 Турецкая лира",
}

# Базовый URL для получения курсов валют (бесплатный API без ключа)
EXCHANGE_RATE_API_URL = "https://api.exchangerate.host/latest"


async def get_exchange_rate(base_currency: str, target_currency: str) -> float | None:
    """
    Получает курс обмена между двумя валютами.

    Args:
        base_currency: Базовая валюта (например, "USD")
        target_currency: Целевая валюта (например, "EUR")

    Returns:
        Курс обмена (сколько единиц целевой валюты за 1 единицу базовой)
        или None в случае ошибки
    """
    if base_currency == target_currency:
        return 1.0

    if base_currency not in SUPPORTED_CURRENCIES:
        logger.warning("Неподдерживаемая базовая валюта: %s", base_currency)
        return None

    if target_currency not in SUPPORTED_CURRENCIES:
        logger.warning("Неподдерживаемая целевая валюта: %s", target_currency)
        return None

    try:
        async with aiohttp.ClientSession() as session:
            # Получаем курсы относительно базовой валюты
            url = f"{EXCHANGE_RATE_API_URL}?base={base_currency}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    logger.error(
                        "Ошибка при получении курса валют: статус %s", response.status
                    )
                    return None

                data: dict[str, Any] = await response.json()

                if not data.get("success", False):
                    logger.error("API вернул ошибку: %s", data.get("error", "Unknown"))
                    return None

                rates = data.get("rates", {})
                if target_currency not in rates:
                    logger.error(
                        "Валюта %s не найдена в ответе API", target_currency
                    )
                    return None

                rate = float(rates[target_currency])
                logger.info(
                    "Получен курс: 1 %s = %.4f %s",
                    base_currency,
                    rate,
                    target_currency,
                )
                return rate

    except aiohttp.ClientError as e:
        logger.error("Ошибка сети при получении курса валют: %s", e, exc_info=True)
        return None
    except (ValueError, KeyError) as e:
        logger.error("Ошибка парсинга ответа API: %s", e, exc_info=True)
        return None
    except Exception as e:
        logger.error("Неожиданная ошибка при получении курса: %s", e, exc_info=True)
        return None


async def convert_currency(
    amount: float, base_currency: str, target_currency: str
) -> tuple[float | None, float | None]:
    """
    Конвертирует сумму из одной валюты в другую.

    Args:
        amount: Сумма для конвертации
        base_currency: Исходная валюта
        target_currency: Целевая валюта

    Returns:
        Кортеж (конвертированная сумма, курс обмена)
        или (None, None) в случае ошибки
    """
    rate = await get_exchange_rate(base_currency, target_currency)
    if rate is None:
        return None, None

    converted_amount = amount * rate
    return converted_amount, rate


def format_currency_result(
    amount: float,
    base_currency: str,
    converted_amount: float,
    target_currency: str,
    rate: float,
) -> str:
    """
    Форматирует результат конвертации валют для отправки пользователю.

    Args:
        amount: Исходная сумма
        base_currency: Исходная валюта
        converted_amount: Конвертированная сумма
        target_currency: Целевая валюта
        rate: Курс обмена

    Returns:
        Отформатированное сообщение
    """
    base_name = SUPPORTED_CURRENCIES.get(base_currency, base_currency)
    target_name = SUPPORTED_CURRENCIES.get(target_currency, target_currency)

    return (
        f"💱 Конвертация валют\n\n"
        f"📊 {amount:,.2f} {base_currency} ({base_name})\n"
        f"➡️ {converted_amount:,.2f} {target_currency} ({target_name})\n\n"
        f"📈 Курс: 1 {base_currency} = {rate:.4f} {target_currency}"
    )
