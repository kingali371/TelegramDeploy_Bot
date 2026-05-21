# app.py
import os
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

# إعدادات البوت - باستخدام التوكن فقط
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # هذا هو المطلوب

# إنشاء عميل البوت (لا حاجة لـ SESSION_STRING)
telegram_app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN  # فقط التوكن كافٍ
)

@telegram_app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ البوت يعمل بنجاح على Render!")

@telegram_app.on_message(filters.command("ping"))
async def ping(client, message):
    await message.reply("🏓 Pong!")

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port, debug=False)

def run_bot():
    telegram_app.run()

if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    # تشغيل البوت في الخيط الرئيسي
    run_bot()
