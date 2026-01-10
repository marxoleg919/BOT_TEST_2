"""
Роутер для команды /convert.

Обрабатывает команду конвертации валют с использованием inline-кнопок для выбора валют.
"""

import logging
from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.bot.services.currency import (
    SUPPORTED_CURRENCIES,
    convert_currency,
    format_currency_result,
)
from src.bot.utils.formatting import format_user_for_log

logger = logging.getLogger("bot")

router = Router()


class ConvertStates(StatesGroup):
    """Состояния для конечного автомата конвертации валют."""
    waiting_for_currency = State()  # Ожидание выбора валюты
    waiting_for_amount = State()   # Ожидание ввода суммы


def get_currency_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру с 10 поддерживаемыми валютами.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками валют
    """
    # Получаем список из 10 валют
    currencies = list(SUPPORTED_CURRENCIES.items())[:10]
    
    # Создаем кнопки по 2 в ряд
    buttons = []
    for i in range(0, len(currencies), 2):
        row = []
        # Добавляем первую валюту в ряду
        code1, name1 = currencies[i]
        row.append(InlineKeyboardButton(
            text=f"{code1} - {name1}",
            callback_data=f"currency:{code1}"
        ))
        
        # Добавляем вторую валюту, если есть
        if i + 1 < len(currencies):
            code2, name2 = currencies[i + 1]
            row.append(InlineKeyboardButton(
                text=f"{code2} - {name2}",
                callback_data=f"currency:{code2}"
            ))
        
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /convert.
    
    Отправляет пользователю меню с выбором валюты.
    """
    logger.info("Команда /convert от пользователя: %s", format_user_for_log(message))
    
    # Отправляем сообщение с клавиатурой выбора валюты
    keyboard = get_currency_keyboard()
    await message.answer(
        "💱 Выберите валюту для конвертации:",
        reply_markup=keyboard
    )
    
    # Устанавливаем состояние ожидания выбора валюты
    await state.set_state(ConvertStates.waiting_for_currency)


@router.callback_query(ConvertStates.waiting_for_currency, F.data.startswith("currency:"))
async def callback_currency_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора валюты через inline-кнопки.
    
    Args:
        callback: CallbackQuery объект
        state: FSMContext для управления состоянием
    """
    # Извлекаем код валюты из callback_data
    currency_code = callback.data.split(":")[1]
    
    # Сохраняем выбранную валюту в состоянии
    await state.update_data(selected_currency=currency_code)
    
    # Отправляем подтверждение выбора
    currency_name = SUPPORTED_CURRENCIES.get(currency_code, currency_code)
    await callback.message.edit_text(
        f"✅ Вы выбрали валюту: {currency_code} ({currency_name})\n\n"
        f"📝 Теперь введите сумму для конвертации:"
    )
    
    # Переходим к следующему состоянию - ожидание ввода суммы
    await state.set_state(ConvertStates.waiting_for_amount)
    
    # Отвечаем на callback, чтобы убрать "часики"
    await callback.answer()


@router.message(ConvertStates.waiting_for_amount)
async def process_amount_input(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода суммы для конвертации.
    
    Args:
        message: Сообщение с суммой
        state: FSMContext для управления состоянием
    """
    # Получаем выбранную валюту из состояния
    user_data = await state.get_data()
    currency_code = user_data.get("selected_currency")
    
    if not currency_code:
        # Если каким-то образом потеряли валюту, начинаем сначала
        await message.answer("❌ Произошла ошибка. Пожалуйста, начните сначала с команды /convert")
        await state.clear()
        return
    
    # Проверяем, что введено число
    try:
        amount = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer("❌ Пожалуйста, введите корректное число для суммы.")
        return
    
    # Проверяем, что сумма положительная
    if amount <= 0:
        await message.answer("❌ Сумма должна быть положительным числом.")
        return
    
    # Отправляем сообщение о начале конвертации
    await message.answer("⏳ Получаю актуальный курс валют...")
    
    # Выполняем конвертацию в USD как пример
    converted_amount, rate = await convert_currency(
        amount, currency_code, "USD"  # Конвертируем в USD для примера
    )
    
    # Проверяем результат
    if converted_amount is None or rate is None:
        logger.error(
            "Ошибка конвертации валют: amount=%s, base=%s, target=USD",
            amount,
            currency_code,
        )
        await message.answer(
            "❌ Не удалось получить курс валют. Попробуйте позже.\n\n"
            "Возможные причины:\n"
            "• Проблемы с подключением к серверу курсов валют\n"
            "• Временная недоступность API"
        )
        await state.clear()
        return
    
    # Форматируем и отправляем результат
    result_text = format_currency_result(
        amount, currency_code, converted_amount, "USD", rate
    )
    await message.answer(result_text)
    
    logger.info(
        "Конвертация выполнена: %.2f %s -> %.2f USD (курс: %.4f)",
        amount,
        currency_code,
        converted_amount,
        rate,
    )
    
    # Очищаем состояние
    await state.clear()
