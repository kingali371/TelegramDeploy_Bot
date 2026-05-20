# app.py
import os
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

# Flask app - ضروري لـ gunicorn
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive!"

@web_app.route('/health')
def health():
    return "OK", 200

# إعدادات البوت
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Pyrogram client
telegram_app = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@telegram_app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ البوت يعمل بنجاح على Render!")

@telegram_app.on_message(filters.command("ping"))
async def ping(client, message):
    await message.reply("🏓 Pong!")

def run_flask():
    """تشغيل Flask"""
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port, debug=False)

def run_bot():
    """تشغيل البوت"""
    telegram_app.run()

if __name__ == "__main__":
    # تشغيل Flask و Pyrogram معًا
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    run_bot()
