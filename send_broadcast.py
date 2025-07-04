# send_broadcast.py
import asyncio
from telegram import Bot
from database import SessionLocal, User
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def broadcast(message):
    db = SessionLocal()
    users = db.query(User).all()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id, text=message)
            print(f"[✅] Sent to {user.user_id}")
        except Exception as e:
            print(f"[❌] Failed to send to {user.user_id}: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python send_broadcast.py 'your message'")
    else:
        asyncio.run(broadcast(sys.argv[1]))
