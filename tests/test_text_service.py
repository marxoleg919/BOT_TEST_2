"""
Тесты для сервисов работы с текстами (`src.bot.services.text`).
"""

from aiogram.types import User

from src.bot.services.text import (
    make_echo_reply,
    make_help_message,
    make_language_message,
    make_premium_message,
    make_profile_message,
    make_start_message,
)


def test_make_echo_reply_returns_same_text_for_non_numbers() -> None:
    """Для нечислового текста функция должна возвращать тот же самый текст."""
    text = "Привет, бот!"

    result = make_echo_reply(text)

    assert result == text


def test_make_echo_reply_adds_100_for_integer_text() -> None:
    """
    Если пользователь присылает число, бот должен вернуть число + 100.
    """
    input_text = "42"

    result = make_echo_reply(input_text)

    assert result == "142"


def test_make_echo_reply_ignores_spaces_around_number() -> None:
    """Пробелы вокруг числа не должны мешать интерпретации как числа."""
    input_text = "   5  "

    result = make_echo_reply(input_text)

    assert result == "105"


def test_make_start_message_contains_expected_phrases() -> None:
    """Стартовое сообщение должно содержать приветствие и упоминание нейросетей."""
    message = make_start_message()

    assert "Привет" in message
    assert "нейросет" in message  # часть слова, чтобы не завязываться на регистр/форму


def test_make_premium_message_mentions_premium() -> None:
    """Сообщение о премиум-подписке должно содержать ключевые подсказки."""
    message = make_premium_message()

    assert "Premium" in message or "Премиум" in message
    assert "подписк" in message  # часть слова "подписка"


def test_make_language_message_lists_languages() -> None:
    """Сообщение выбора языка должно перечислять доступные языки."""
    message = make_language_message()

    assert "Русский" in message
    assert "English" in message
    assert "Deutsch" in message


def test_make_help_message_contains_commands() -> None:
    """Сообщение помощи должно содержать список основных команд."""
    message = make_help_message()

    for command in ("/start", "/profile", "/premium", "/language", "/help"):
        assert command in message


def test_make_profile_message_when_user_is_none() -> None:
    """Если пользователь не передан, должно вернуться сообщение об ошибке."""
    message = make_profile_message(None)

    assert "Не удалось" in message


def test_make_profile_message_with_full_user_data() -> None:
    """Профиль должен корректно собирать данные пользователя."""
    user = User(
        id=123,
        is_bot=False,
        first_name="Иван",
        last_name="Иванов",
        username="ivan_test",
        language_code="ru",
    )

    message = make_profile_message(user)

    assert "123" in message
    assert "Иван Иванов" in message
    assert "@ivan_test" in message
    assert "ru" in message


def test_make_profile_message_without_username_and_last_name() -> None:
    """Функция должна корректно обрабатывать отсутствие username и фамилии."""
    user = User(
        id=456,
        is_bot=False,
        first_name="Мария",
        last_name=None,
        username=None,
        language_code=None,
    )

    message = make_profile_message(user)

    assert "Мария" in message
    assert "не указан" in message  # username/язык помечены как не указанные


