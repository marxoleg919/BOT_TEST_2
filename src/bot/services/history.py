"""
Репозитории истории диалогов для режима ChatGPT.

Содержит общий интерфейс и две реализации:
- InMemoryChatHistoryRepository — для локального запуска;
- RedisChatHistoryRepository — для масштабируемого хранилища с TTL.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Protocol

from redis.asyncio import Redis


Message = dict[str, str]


@dataclass(frozen=True)
class HistorySettings:
    """Настройки хранения истории диалогов."""

    max_messages: int = 20
    ttl_seconds: int = 60 * 60 * 24  # 24 часа по умолчанию


class ChatHistoryRepository(Protocol):
    """Контракт репозитория истории диалогов."""

    async def start_session(self, user_id: int) -> None: ...

    async def stop_session(self, user_id: int) -> None: ...

    async def is_active(self, user_id: int) -> bool: ...

    async def add_user_message(self, user_id: int, content: str) -> None: ...

    async def add_assistant_message(self, user_id: int, content: str) -> None: ...

    async def get_history(self, user_id: int) -> list[Message]: ...

    async def trim(self, user_id: int) -> None: ...

    async def aclose(self) -> None: ...


class InMemoryChatHistoryRepository(ChatHistoryRepository):
    """
    Простое in-memory хранилище.

    Подходит для локальной отладки и одиночного процесса.
    """

    def __init__(self, settings: HistorySettings) -> None:
        self._settings = settings
        self._store: dict[int, list[Message]] = {}
        self._expires_at: dict[int, float] = {}

    async def start_session(self, user_id: int) -> None:
        self._store[user_id] = []
        self._expires_at[user_id] = self._now() + self._settings.ttl_seconds

    async def stop_session(self, user_id: int) -> None:
        self._store.pop(user_id, None)
        self._expires_at.pop(user_id, None)

    async def is_active(self, user_id: int) -> bool:
        return self._cleanup_and_check(user_id)

    async def add_user_message(self, user_id: int, content: str) -> None:
        await self._ensure_session(user_id)
        self._store[user_id].append({"role": "user", "content": content})
        await self.trim(user_id)

    async def add_assistant_message(self, user_id: int, content: str) -> None:
        await self._ensure_session(user_id)
        self._store[user_id].append({"role": "assistant", "content": content})
        await self.trim(user_id)

    async def get_history(self, user_id: int) -> list[Message]:
        if not self._cleanup_and_check(user_id):
            return []
        return list(self._store[user_id])

    async def trim(self, user_id: int) -> None:
        if user_id not in self._store:
            return
        max_messages = self._settings.max_messages
        if max_messages <= 0:
            return
        history = self._store[user_id]
        if len(history) > max_messages:
            self._store[user_id] = history[-max_messages:]

    async def aclose(self) -> None:
        # Ничего закрывать не нужно
        return

    async def _ensure_session(self, user_id: int) -> None:
        if not self._cleanup_and_check(user_id):
            await self.start_session(user_id)

    def _cleanup_and_check(self, user_id: int) -> bool:
        expires_at = self._expires_at.get(user_id)
        if expires_at is None:
            return False
        if expires_at < self._now():
            # TTL истёк — очищаем
            self._store.pop(user_id, None)
            self._expires_at.pop(user_id, None)
            return False
        return True

    @staticmethod
    def _now() -> float:
        return time.monotonic()


class RedisChatHistoryRepository(ChatHistoryRepository):
    """
    Хранилище истории в Redis с TTL.

    Хранит каждое сообщение в JSON-формате в списке, поддерживает обрезку длины
    и обновление TTL при каждом обращении.
    """

    def __init__(self, redis: Redis, settings: HistorySettings) -> None:
        self._redis = redis
        self._settings = settings
        self._key_prefix = "chat_history:"

    async def start_session(self, user_id: int) -> None:
        key = self._key(user_id)
        await self._redis.delete(key)

    async def stop_session(self, user_id: int) -> None:
        await self._redis.delete(self._key(user_id))

    async def is_active(self, user_id: int) -> bool:
        return bool(await self._redis.exists(self._key(user_id)))

    async def add_user_message(self, user_id: int, content: str) -> None:
        await self._append(user_id, {"role": "user", "content": content})

    async def add_assistant_message(self, user_id: int, content: str) -> None:
        await self._append(user_id, {"role": "assistant", "content": content})

    async def get_history(self, user_id: int) -> list[Message]:
        key = self._key(user_id)
        raw_items = await self._redis.lrange(key, 0, -1)
        history: list[Message] = []
        for raw in raw_items:
            try:
                history.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        if history:
            await self._touch_ttl(key)
        return history

    async def trim(self, user_id: int) -> None:
        max_messages = self._settings.max_messages
        if max_messages <= 0:
            return
        key = self._key(user_id)
        # Оставляем последние max_messages
        await self._redis.ltrim(key, -max_messages, -1)
        await self._touch_ttl(key)

    async def aclose(self) -> None:
        close = getattr(self._redis, "aclose", None)
        if callable(close):
            await close()
            return
        self._redis.close()
        wait_closed = getattr(self._redis, "wait_closed", None)
        if callable(wait_closed):
            await wait_closed()

    async def _append(self, user_id: int, message: Message) -> None:
        key = self._key(user_id)
        await self._redis.rpush(key, json.dumps(message, ensure_ascii=False))
        await self.trim(user_id)
        await self._touch_ttl(key)

    async def _touch_ttl(self, key: str) -> None:
        ttl = self._settings.ttl_seconds
        if ttl > 0:
            await self._redis.expire(key, ttl)

    def _key(self, user_id: int) -> str:
        return f"{self._key_prefix}{user_id}"


def build_history_repository(
    backend: str,
    settings: HistorySettings,
    redis_url: str | None = None,
) -> ChatHistoryRepository:
    """
    Фабрика репозитория истории.

    backend: "redis" или "memory". Если указан redis, но URL отсутствует,
    автоматически падаем назад на InMemory.
    """
    if backend.lower() == "redis" and redis_url:
        redis_client = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        return RedisChatHistoryRepository(redis_client, settings)
    return InMemoryChatHistoryRepository(settings)
