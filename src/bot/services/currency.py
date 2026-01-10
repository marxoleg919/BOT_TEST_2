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
# Используем open.er-api.com - более надежный бесплатный API
EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest"


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
            # Формат URL: https://open.er-api.com/v6/latest/{BASE_CURRENCY}
            url = f"{EXCHANGE_RATE_API_URL}/{base_currency}"
            logger.info("Запрос курса валют: %s -> %s, URL: %s", base_currency, target_currency, url)
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    response_text = await response.text()
                    logger.error(
                        "Ошибка при получении курса валют: статус %s, URL: %s, ответ: %s",
                        response.status,
                        url,
                        response_text[:200],  # Первые 200 символов ответа
                    )
                    return None

                data: dict[str, Any] = await response.json()
                logger.info("Ответ API получен: result=%s, base_code=%s", 
                           data.get("result"), data.get("base_code"))

                # Проверяем результат API (формат: {"result": "success", "rates": {...}})
                if data.get("result") != "success":
                    error_msg = data.get("error", "Unknown error")
                    logger.error("API вернул ошибку: %s, полный ответ: %s", error_msg, data)
                    return None

                # Получаем курсы валют
                rates = data.get("rates")
                
                if not rates:
                    logger.error("Не найдено поле rates в ответе API. Ответ: %s", data)
                    return None

                # Проверяем наличие целевой валюты в курсах
                if target_currency not in rates:
                    available_currencies = list(rates.keys())[:20]
                    logger.error(
                        "Валюта %s не найдена в ответе API. Доступные валюты (первые 20): %s",
                        target_currency,
                        ", ".join(available_currencies),
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
        logger.error("Ошибка сети при получении курса валют: %s, тип: %s", 
                    e, type(e).__name__, exc_info=True)
        return None
    except (ValueError, KeyError) as e:
        logger.error("Ошибка парсинга ответа API: %s, тип: %s", e, type(e).__name__, exc_info=True)
        return None
    except Exception as e:
        logger.error("Неожиданная ошибка при получении курса: %s, тип: %s", 
                    e, type(e).__name__, exc_info=True)
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
