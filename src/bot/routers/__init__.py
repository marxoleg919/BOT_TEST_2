"""
Пакет с Telegram-роутерами (маршрутизация и обработчики апдейтов).

Бизнес-логика должна находиться в слое services.
"""

from aiogram import Router

from . import chatgpt, echo, start, profile, premium, language, help


def get_main_router() -> Router:
    """
    Возвращает корневой роутер приложения, в который подключены
    все остальные под-роутеры.
    """
    router = Router()
    # Подключаем роутеры команд (важен порядок - более специфичные команды первыми)
    router.include_router(start.router)
    router.include_router(profile.router)
    router.include_router(premium.router)
    router.include_router(language.router)
    router.include_router(help.router)
    # Роутер ChatGPT подключаем перед echo, чтобы перехватывать сообщения в режиме диалога
    router.include_router(chatgpt.router)
    # Эхо-роутер подключаем последним, чтобы он обрабатывал только неизвестные сообщения
    router.include_router(echo.router)
    return router


