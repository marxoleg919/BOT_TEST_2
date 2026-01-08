## Телеграм-бот (aiogram) — учебный эхо-бот

Простой эхо-бот на `aiogram`, оформленный по профессиональной структуре проекта:

- конфигурация и переменные окружения;
- раздельные модули для роутеров, сервисов и утилит;
- логирование в консоль и в файл.

### Требования

- Python 3.10+  
- Установленный Git (опционально)  

### Установка и запуск на Windows

1. **Клонируйте/разместите проект** в папке, где вы хотите с ним работать.

2. **Создайте и активируйте виртуальное окружение**:

```powershell
cd "C:\Users\лингвариум\Documents\BOT_TEST_2"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Установите зависимости**:

```powershell
pip install -r requirements.txt
```

4. **Создайте файл `.env` на основе примера**:

Скопируйте `.env.example` в `.env` и впишите токен бота:

```env
TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН_ОТ_BOTFATHER
OPENROUTER_API_KEY=ВАШ_КЛЮЧ_OPENROUTER  # Опционально, нужен для команды /chatgpt
LLM_MODEL=mistralai/mistral-7b-instruct:free
# OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
# LLM_TIMEOUT_SEC=20
# LLM_RETRIES=3
# LLM_REFERER=https://example.com
# CHAT_HISTORY_BACKEND=memory  # или redis
# REDIS_URL=redis://localhost:6379/0
# HISTORY_MAX_MESSAGES=20
# HISTORY_TTL_SEC=86400
```

> **Примечание:** `OPENROUTER_API_KEY` опционален. Если вы не планируете использовать команду `/chatgpt`, можете не указывать этот ключ. Получить ключ можно на [openrouter.ai](https://openrouter.ai/).

5. **Запустите бота**:

```powershell
python -m src.bot
```

или (временно, для совместимости):

```powershell
python bot.py
```

### Запуск на macOS / Linux

```bash
cd /путь/к/проекту
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # либо создайте .env вручную
python -m src.bot
```

### Команды бота

- `/start` - Перезапустить бота (Выбрать нейросеть)
- `/chatgpt` - Активировать режим ChatGPT (общение с LLM через OpenRouter)
- `/stop` - Выйти из режима ChatGPT
- `/profile` - Просмотреть профиль
- `/premium` - Информация о Premium подписке
- `/language` - Изменить язык интерфейса
- `/help` - Показать справку

### Логи

- Логи пишутся в папку `logs`, файл `logs/bot.log`.
- Логируются запуски бота, команды и текстовые сообщения пользователей (без конфиденциальных данных).

### Переменные окружения

Минимально необходимые:
- `TELEGRAM_BOT_TOKEN` — токен бота.

Для работы с LLM:
- `OPENROUTER_API_KEY` — ключ OpenRouter (для `/chatgpt`).
- `LLM_MODEL` — идентификатор модели (по умолчанию `mistralai/mistral-7b-instruct:free`).
- `OPENROUTER_API_URL` — URL API (по умолчанию OpenRouter).
- `LLM_TIMEOUT_SEC` — таймаут запроса к LLM (по умолчанию 20).
- `LLM_RETRIES` — количество ретраев на 5xx/сетевые ошибки (по умолчанию 3).
- `LLM_REFERER` — опциональный реферер для аналитики.

Хранилище истории диалогов:
- `CHAT_HISTORY_BACKEND` — `memory` или `redis` (по умолчанию `memory`).
- `REDIS_URL` — строка подключения к Redis (нужна, если выбран backend `redis`).
- `HISTORY_MAX_MESSAGES` — лимит сообщений истории на пользователя (по умолчанию 20).
- `HISTORY_TTL_SEC` — TTL истории в секундах (по умолчанию 86400, 24 часа).


