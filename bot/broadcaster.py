# broadcaster.py
import asyncio
from telegram import Bot
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def broadcast_message(user_ids, message):
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message)
            print(f"[✅] Sent to {user_id}")
        except Exception as e:
            print(f"[❌] Failed to send to {user_id}: {e}")
