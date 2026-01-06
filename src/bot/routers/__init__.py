"""
Пакет с Telegram-роутерами (маршрутизация и обработчики апдейтов).

Бизнес-логика должна находиться в слое services.
"""

from aiogram import Router

from . import echo


def get_main_router() -> Router:
    """
    Возвращает корневой роутер приложения, в который подключены
    все остальные под-роутеры.
    """
    router = Router()
    router.include_router(echo.router)
    return router


