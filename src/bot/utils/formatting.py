"""
Утилиты форматирования для логирования и отображения.

Общие функции, используемые в разных частях приложения.
"""

from aiogram.types import Message, User


def format_user_for_log(message: Message) -> str:
    """
    Формирует строку с информацией о пользователе для логирования.

    Args:
        message: Объект сообщения Telegram

    Returns:
        Строка вида "id=123, @username, имя='Имя Фамилия'"
    """
    user = message.from_user
    if user is None:
        return "неизвестный пользователь"

    username = f"@{user.username}" if user.username else "без username"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return f"id={user.id}, {username}, имя='{full_name}'"


def format_user_profile(user: User | None) -> str:
    """
    Формирует текст профиля пользователя для отображения.

    Args:
        user: Объект пользователя Telegram или None

    Returns:
        Форматированная строка с информацией о профиле
    """
    if user is None:
        return "❌ Не удалось получить информацию о профиле."

    username = f"@{user.username}" if user.username else "не указан"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "не указано"

    return (
        f"👤 Профиль\n\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Имя: {full_name}\n"
        f"📱 Username: {username}\n"
        f"🌐 Язык: {user.language_code or 'не указан'}"
    )

