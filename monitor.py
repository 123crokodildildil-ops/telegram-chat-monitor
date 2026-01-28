import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import User
import requests
from dotenv import load_dotenv

load_dotenv()

# Данные из переменных окружения
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
