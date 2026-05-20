# app.py
import os
import asyncio
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive!"

@web_app.route('/health')
def health():
    return "OK", 200

# إعدادات البوت - استخدم BOT_TOKEN بدلاً من SESSION_STRING
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# إذا كان لديك SESSION_STRING موجودة فعلية
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Pyrogram client
if BOT_TOKEN:
    # استخدام البوت العادي
    telegram_app = Client(
        "bot_session",
        bot_token=BOT_TOKEN,
        api_id=int(os.environ.get("API_ID", 0)),
        api_hash=os.environ.get("API_HASH", "")
    )
else:
    # استخدام سترينغ الجلسة
    telegram_app = Client(
        "bot_session",
        api_id=int(os.environ.get("API_ID", 0)),
        api_hash=os.environ.get("API_HASH", ""),
        session_string=SESSION_STRING
    )

@telegram_app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ البوت يعمل بنجاح على Render!")

@telegram_app.on_message(filters.command("ping"))
async def ping(client, message):
    await message.reply("🏓 Pong!")

# متغير عام للتحكم
bot_running = False

def run_bot():
    """تشغيل البوت"""
    global bot_running
    if not bot_running:
        bot_running = True
        telegram_app.run()

# تشغيل البوت في الخلفية عند استيراد الوحدة
if not os.environ.get("GUNICORN_RUNNING"):
    # لمنع التشغيل المزدوج
    os.environ["GUNICORN_RUNNING"] = "1"
    thread = Thread(target=run_bot, daemon=True)
    thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port, debug=False)
