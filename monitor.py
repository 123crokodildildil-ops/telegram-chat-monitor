import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import User
import requests
from dotenv import load_dotenv

load_dotenv()

# Данные из .env
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')
N8N_WEBHOOK = os.getenv('N8N_WEBHOOK_URL')

client = TelegramClient('session', API_ID, API_HASH)

async def check_dialogs():
    await client.start(phone=PHONE)
    
    dialogs_to_check = []
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    # Получаем все диалоги
    async for dialog in client.iter_dialogs():
        # Только личные чаты с людьми
        if isinstance(dialog.entity, User) and not dialog.entity.bot:
            # Получаем последнее сообщение
            async for message in client.iter_messages(dialog, limit=1):
                # Если последнее сообщение от собеседника (не от вас)
                if not message.out and message.date < cutoff_time:
                    dialogs_to_check.append({
                        'name': dialog.name or 'Unknown',
                        'username': dialog.entity.username or 'no_username',
                        'user_id': dialog.entity.id,
                        'last_message': message.text or '[media]',
                        'hours_ago': int((datetime.now() - message.date).total_seconds() / 3600),
                        'date': message.date.strftime('%Y-%m-%d %H:%M')
                    })
                break
    
    # Отправляем данные в n8n
    if dialogs_to_check:
        response = requests.post(N8N_WEBHOOK, json={'dialogs': dialogs_to_check})
        print(f"Отправлено {len(dialogs_to_check)} диалогов в n8n")
    else:
        print("Нет диалогов требующих внимания")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(check_dialogs())
```

Нажмите **Commit changes**

---

#### **Файл 3: `Procfile`**

Имя файла: `Procfile` (без расширения!)

Содержимое:
```
worker: while true; do python monitor.py; sleep 86400; done
```

Это запустит скрипт раз в сутки (86400 секунд = 24 часа)

Нажмите **Commit changes**

---

#### **Файл 4: `runtime.txt`**

Имя файла: `runtime.txt`

Содержимое:
```
python-3.11.0
```

Нажмите **Commit changes**

---

**✅ Готово:** В репозитории 4 файла

---

### Шаг 3: Разворачиваем на Railway

1. Перейдите на https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Выберите репозиторий `telegram-chat-monitor`
4. Railway начнёт деплой (подождите 2-3 минуты)

**⚠️ Деплой упадёт с ошибкой** — это нормально, нужно добавить переменные окружения.

---

### Шаг 4: Добавляем переменные окружения

1. В Railway нажмите на развёрнутый сервис
2. Перейдите в **Variables**
3. Нажмите **Add Variable** и добавьте:
```
TELEGRAM_API_ID = [ваш api_id из my.telegram.org]
TELEGRAM_API_HASH = [ваш api_hash]
TELEGRAM_PHONE = [номер телефона аккаунта рассылок в формате +79123456789]
N8N_WEBHOOK_URL = [пока оставьте пустым, заполним позже]
```

4. После добавления всех переменных нажмите **Deploy** (или он перезапустится сам)

---

### Шаг 5: Авторизация Telegram

1. В Railway перейдите в **Deployments**
2. Кликните на последний деплой → **View Logs**
3. Скрипт запросит **код подтверждения**
4. Код придёт в Telegram на аккаунт рассылок
5. **Проблема:** В Railway нельзя вводить код интерактивно

**Решение:** Авторизуемся локально, потом загрузим session-файл.

---

## ⚡ Упрощённый путь: Авторизация локально

### Шаг 1: Установите Python на компьютер

- **Windows:** https://www.python.org/downloads/ (галочка "Add to PATH")
- **Mac:** `brew install python3` (если есть Homebrew) или с python.org

### Шаг 2: Создайте папку и файлы

1. Создайте папку `telegram-monitor` на рабочем столе
2. Скопируйте туда файлы `monitor.py` и `requirements.txt` из GitHub
3. Создайте файл `.env` со своими данными:
```
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash
TELEGRAM_PHONE=+79123456789
N8N_WEBHOOK_URL=http://test.com
