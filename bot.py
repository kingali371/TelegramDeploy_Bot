import os
from pyrogram import Client, filters

# جلب المتغيرات من البيئة
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

# إنشاء العميل
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("✅ البوت يعمل بنجاح على Render!")

@app.on_message(filters.text)
async def echo(client, message):
    await message.reply(f"قلت: {message.text}")

# نقطة البداية
if __name__ == "__main__":
    print("🚀 جاري تشغيل البوت...")
    app.run()
