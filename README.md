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
```

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

### Логи

- Логи пишутся в папку `logs`, файл `logs/bot.log`.
- Логируются запуски бота, команды `/start` и текстовые сообщения пользователей (без конфиденциальных данных).


