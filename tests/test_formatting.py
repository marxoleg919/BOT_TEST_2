"""
Тесты для утилит форматирования (`src.bot.utils.formatting`).
"""

from aiogram.types import User

from src.bot.utils.formatting import format_user_profile


def test_format_user_profile_when_user_is_none() -> None:
    """Если пользователь не передан, должно вернуться сообщение об ошибке."""
    message = format_user_profile(None)

    assert "Не удалось" in message


def test_format_user_profile_with_full_user_data() -> None:
    """Профиль должен корректно собирать данные пользователя."""
    user = User(
        id=123,
        is_bot=False,
        first_name="Иван",
        last_name="Иванов",
        username="ivan_test",
        language_code="ru",
    )

    message = format_user_profile(user)

    assert "123" in message
    assert "Иван Иванов" in message
    assert "@ivan_test" in message
    assert "ru" in message


def test_format_user_profile_without_username_and_last_name() -> None:
    """Функция должна корректно обрабатывать отсутствие username и фамилии."""
    user = User(
        id=456,
        is_bot=False,
        first_name="Мария",
        last_name=None,
        username=None,
        language_code=None,
    )

    message = format_user_profile(user)

    assert "Мария" in message
    assert "не указан" in message  # username/язык помечены как не указанные

