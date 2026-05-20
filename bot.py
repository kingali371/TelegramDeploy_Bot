import os
import time
import asyncio
import logging
from datetime import datetime
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
from keep_alive import keep_alive

# ========== الإعدادات المتقدمة ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== استيراد المتغيرات ==========
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

# ========== فحص المتغيرات ==========
if not all([API_ID, API_HASH, SESSION_STRING]):
    raise ValueError("❌ المتغيرات البيئية غير مكتملة!")

# ========== إنشاء البوت ==========
class SuperBot:
    def __init__(self):
        self.start_time = time.time()
        self.app = Client(
            name="SuperBot",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION_STRING,
            sleep_threshold=60,  # مهلة النوم
            workers=100,  # عدد العمال
            workdir="./sessions",
            plugins=dict(root="plugins")  # مجلد الإضافات
        )
        self._setup_handlers()
    
    def _setup_handlers(self):
        """إعداد معالجات الأوامر"""
        
        @self.app.on_message(filters.command("start") & filters.private)
        async def start_command(client, message: Message):
            await message.reply_text(
                f"🔥 **مرحباً {message.from_user.mention}!**\n\n"
                "✅ البوت يعمل بقوة على Render\n"
                "⚡ السرعة: عالية\n"
                "🛡️ الحماية: نشطة\n\n"
                "📋 الأوامر المتاحة:\n"
                "/start - بدء التشغيل\n"
                "/ping - فحص السرعة\n"
                "/stats - إحصائيات البوت\n"
                "/broadcast - رسالة جماعية (للمالك فقط)\n"
                "/restart - إعادة تشغيل (للمالك فقط)"
            )
        
        @self.app.on_message(filters.command("ping"))
        async def ping_command(client, message: Message):
            start = time.time()
            msg = await message.reply_text("⚡ جاري فحص السرعة...")
            end = time.time()
            ping_time = round((end - start) * 1000, 2)
            
            await msg.edit_text(
                f"🏓 **Pong!**\n"
                f"⏱️ زمن الاستجابة: `{ping_time}ms`\n"
                f"🚀 السرعة: ممتازة"
            )
        
        @self.app.on_message(filters.command("stats"))
        async def stats_command(client, message: Message):
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            await message.reply_text(
                f"📊 **إحصائيات البوت**\n\n"
                f"⏰ مدة التشغيل: `{hours}h {minutes}m`\n"
                f"🔄 عدد العمال: `100`\n"
                f"🛡️ الحماية: نشطة\n"
                f"📡 الخادم: Render Cloud"
            )
        
        @self.app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
        async def broadcast_command(client, message: Message):
            if len(message.command) < 2:
                return await message.reply("⚠️ استخدم: /broadcast <الرسالة>")
            
            broadcast_msg = " ".join(message.command[1:])
            success = 0
            failed = 0
            
            status_msg = await message.reply("📤 جاري الإرسال...")
            
            async for dialog in client.get_dialogs():
                try:
                    await client.send_message(dialog.chat.id, f"📢 {broadcast_msg}")
                    success += 1
                    await asyncio.sleep(0.5)  # تجنب الحظر
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except:
                    failed += 1
            
            await status_msg.edit_text(
                f"✅ تم الإرسال الجماعي:\n"
                f"👥 ناجح: `{success}`\n"
                f"❌ فشل: `{failed}`"
            )
        
        @self.app.on_message(filters.command("restart") & filters.user(OWNER_ID))
        async def restart_command(client, message: Message):
            await message.reply_text("🔄 جاري إعادة تشغيل البوت...")
            os.system("kill 1")  # إعادة تشغيل Render
        
        # معالج الأخطاء
        @self.app.on_message(filters.all)
        async def handle_all(client, message: Message):
            if message.text and not message.text.startswith("/"):
                logger.info(f"رسالة من {message.from_user.id}: {message.text[:50]}")
    
    async def start_bot(self):
        """تشغيل البوت"""
        try:
            await self.app.start()
            logger.info("✅ تم تشغيل البوت بنجاح!")
            
            # إرسال إشعار للمالك
            if OWNER_ID:
                try:
                    await self.app.send_message(
                        OWNER_ID,
                        f"🚀 **تم تشغيل البوت على Render!**\n"
                        f"📅 الوقت: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                    )
                except:
                    pass
            
            await idle()
            
        except Exception as e:
            logger.error(f"❌ خطأ: {e}")
        finally:
            await self.app.stop()
    
    def run(self):
        """النقطة الرئيسية"""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.start_bot())
        except KeyboardInterrupt:
            logger.info("👋 تم إيقاف البوت")
        except Exception as e:
            logger.error(f"💥 خطأ قاتل: {e}")

# ========== التشغيل ==========
if __name__ == "__main__":
    # تشغيل نظام منع النوم
    keep_alive()
    
    # تشغيل البوت
    bot = SuperBot()
    bot.run()
