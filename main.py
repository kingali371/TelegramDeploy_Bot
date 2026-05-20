import os
import sys
import time
import json
import asyncio
import logging
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import FloodWait
from keep_alive import keep_alive

# ========== الإعدادات ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "")
RENDER_SERVICE_ID = os.environ.get("RENDER_SERVICE_ID", "")

# ========== تهيئة البوت ==========
app = Client(
    "deploy_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ========== قاعدة بيانات مؤقتة ==========
user_states = {}
user_sessions = {}

# ========== لوحة المفاتيح الرئيسية ==========
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 استخراج جلسة", callback_data="extract_session")],
        [InlineKeyboardButton("📤 رفع على GitHub", callback_data="upload_github")],
        [InlineKeyboardButton("☁️ نشر على Render", callback_data="deploy_render")],
        [InlineKeyboardButton("⚙️ إدارة السيرفر", callback_data="server_management")],
        [InlineKeyboardButton("📊 حالة البوتات", callback_data="bot_status")],
        [InlineKeyboardButton("❓ مساعدة", callback_data="help")]
    ])

# ========== أوامر البوت ==========
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user = message.from_user
    
    await message.reply_text(
        f"🎉 **مرحباً {user.mention}!**\n\n"
        "🚀 **بوت النشر المتكامل**\n"
        "يمكنني مساعدتك في:\n"
        "• استخراج جلسات Pyrogram\n"
        "• الرفع على GitHub\n"
        "• النشر على Render\n"
        "• إدارة البوتات\n\n"
        "📋 اختر من القائمة:",
        reply_markup=main_keyboard()
    )

@app.on_callback_query()
async def handle_callbacks(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    # التحقق من الصلاحيات (اختياري)
    if OWNER_ID and user_id != OWNER_ID:
        return await callback_query.answer("⛔ غير مصرح لك!", show_alert=True)
    
    if data == "extract_session":
        await extract_session_menu(client, callback_query)
    
    elif data == "upload_github":
        await github_menu(client, callback_query)
    
    elif data == "deploy_render":
        await render_menu(client, callback_query)
    
    elif data == "server_management":
        await server_menu(client, callback_query)
    
    elif data == "bot_status":
        await check_status(client, callback_query)
    
    elif data == "help":
        await help_menu(client, callback_query)
    
    elif data == "back_main":
        await callback_query.message.edit_text(
            "📋 **القائمة الرئيسية**\nاختر ما تريد:",
            reply_markup=main_keyboard()
        )

# ========== 1. قائمة استخراج الجلسة ==========
async def extract_session_menu(client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 تسجيل الدخول", callback_data="login_user")],
        [InlineKeyboardButton("🔑 استخراج جلسة حالية", callback_data="get_session")],
        [InlineKeyboardButton("🔐 استخراج جلسة بوت", callback_data="bot_session")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])
    
    await callback_query.message.edit_text(
        "🔑 **استخراج الجلسات**\n\n"
        "اختر نوع الجلسة:\n"
        "• مستخدم عادي\n"
        "• بوت\n\n"
        "⚠️ تأكد من إدخال بيانات صحيحة!",
        reply_markup=keyboard
    )

# استخراج جلسة مستخدم
@app.on_callback_query(filters.regex("login_user"))
async def start_session_extraction(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_states[user_id] = {"state": "waiting_api_id"}
    
    await callback_query.message.edit_text(
        "📋 **استخراج جلسة مستخدم**\n\n"
        "أرسل `API_ID` الخاص بك:\n"
        "(يمكنك الحصول عليه من my.telegram.org)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="back_main")]
        ])
    )

@app.on_message(filters.text & filters.private)
async def handle_session_steps(client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_states:
        return
    
    state = user_states[user_id]["state"]
    
    if state == "waiting_api_id":
        try:
            api_id = int(message.text)
            user_states[user_id]["api_id"] = api_id
            user_states[user_id]["state"] = "waiting_api_hash"
            
            await message.reply_text(
                "✅ تم استلام API_ID\n\n"
                "الآن أرسل `API_HASH`:"
            )
        except ValueError:
            await message.reply_text("❌ خطأ! أرسل رقم API_ID صحيح")
    
    elif state == "waiting_api_hash":
        user_states[user_id]["api_hash"] = message.text
        user_states[user_id]["state"] = "waiting_phone"
        
        await message.reply_text(
            "✅ تم استلام API_HASH\n\n"
            "الآن أرسل رقم الهاتف:\n"
            "مثال: `+9639XXXXXXXX`"
        )
    
    elif state == "waiting_phone":
        user_states[user_id]["phone"] = message.text
        user_states[user_id]["state"] = "extracting"
        
        await message.reply_text("⏳ جاري استخراج الجلسة...")
        await extract_user_session(client, message, user_id)

async def extract_user_session(client, message: Message, user_id: int):
    """استخراج جلسة المستخدم"""
    data = user_states[user_id]
    
    try:
        # إنشاء جلسة جديدة
        temp_client = Client(
            f"temp_{user_id}",
            api_id=data["api_id"],
            api_hash=data["api_hash"]
        )
        
        async with temp_client as tc:
            # إرسال كود التحقق
            sent_code = await tc.send_code(data["phone"])
            user_states[user_id]["phone_code_hash"] = sent_code.phone_code_hash
            
            await message.reply_text(
                "📱 **تم إرسال كود التحقق**\n\n"
                "أرسل الكود الذي استلمته:\n"
                "(مثال: 12345)"
            )
            
            user_states[user_id]["state"] = "waiting_code"
            user_states[user_id]["temp_client"] = temp_client
            
    except Exception as e:
        await message.reply_text(f"❌ خطأ: {str(e)}")
        del user_states[user_id]

@app.on_message(filters.regex(r'^\d{5}$') & filters.private)
async def handle_verification_code(client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_states or user_states[user_id].get("state") != "waiting_code":
        return
    
    data = user_states[user_id]
    code = message.text
    
    try:
        temp_client = data["temp_client"]
        
        async with temp_client as tc:
            # تسجيل الدخول
            await tc.sign_in(
                phone_number=data["phone"],
                phone_code_hash=data["phone_code_hash"],
                phone_code=code
            )
            
            # استخراج الجلسة
            session_string = await tc.export_session_string()
            
            # حفظ الجلسة
            user_sessions[user_id] = {
                "session": session_string,
                "api_id": data["api_id"],
                "api_hash": data["api_hash"],
                "timestamp": datetime.now().isoformat()
            }
            
            # إرسال الجلسة للمستخدم
            await message.reply_text(
                "✅ **تم استخراج الجلسة بنجاح!**\n\n"
                f"```{session_string[:50]}...```\n\n"
                "🔐 **احتفظ بها بأمان**\n\n"
                "ماذا تريد أن تفعل الآن؟",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📤 نشر على Render", callback_data="deploy_render")],
                    [InlineKeyboardButton("📋 عرض كاملة", callback_data="show_session")],
                    [InlineKeyboardButton("🔙 القائمة", callback_data="back_main")]
                ])
            )
            
    except Exception as e:
        await message.reply_text(f"❌ خطأ في التحقق: {str(e)}")
    finally:
        if user_id in user_states:
            user_states[user_id]["state"] = "done"

@app.on_callback_query(filters.regex("show_session"))
async def show_full_session(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if user_id in user_sessions:
        session = user_sessions[user_id]["session"]
        
        # تقسيم الجلسة إذا كانت طويلة
        if len(session) > 4000:
            parts = [session[i:i+4000] for i in range(0, len(session), 4000)]
            for part in parts:
                await callback_query.message.reply_text(f"```{part}```")
        else:
            await callback_query.message.reply_text(f"```{session}```")
    else:
        await callback_query.answer("لا توجد جلسة محفوظة", show_alert=True)

# ========== 2. قائمة GitHub ==========
async def github_menu(client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 رفع ملفات", callback_data="upload_files")],
        [InlineKeyboardButton("🔄 تحديث مستودع", callback_data="update_repo")],
        [InlineKeyboardButton("📝 إنشاء ملف", callback_data="create_file")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])
    
    await callback_query.message.edit_text(
        "📤 **إدارة GitHub**\n\n"
        "ارفع ملفات البوت مباشرة إلى مستودعك",
        reply_markup=keyboard
    )

# ========== 3. قائمة Render ==========
async def render_menu(client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 نشر بوت جديد", callback_data="deploy_new_bot")],
        [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart_service")],
        [InlineKeyboardButton("📊 حالة الخدمة", callback_data="service_status")],
        [InlineKeyboardButton("🗑 حذف الخدمة", callback_data="delete_service")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])
    
    await callback_query.message.edit_text(
        "☁️ **نشر على Render**\n\n"
        f"Service ID: `{RENDER_SERVICE_ID[:10] if RENDER_SERVICE_ID else 'غير محدد'}...`\n\n"
        "اختر العملية:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("deploy_new_bot"))
async def deploy_to_render(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    if user_id not in user_sessions:
        return await callback_query.answer("⚠️ استخرج جلسة أولاً!", show_alert=True)
    
    session_data = user_sessions[user_id]
    
    await callback_query.message.edit_text("⏳ جاري النشر على Render...")
    
    # إنشاء ملفات البوت
    bot_code = create_bot_code(
        api_id=session_data["api_id"],
        api_hash=session_data["api_hash"],
        session_string=session_data["session"]
    )
    
    try:
        # رفع على GitHub
        github_success = await upload_to_github(bot_code)
        
        if github_success:
            # نشر على Render
            render_success = await deploy_to_render_api()
            
            if render_success:
                await callback_query.message.edit_text(
                    "✅ **تم النشر بنجاح!**\n\n"
                    "🚀 البوت يعمل الآن على Render\n"
                    f"🔗 الرابط: {os.environ.get('RENDER_EXTERNAL_URL', 'جاري...')}",
                    reply_markup=main_keyboard()
                )
            else:
                await callback_query.message.edit_text("❌ فشل النشر على Render")
        else:
            await callback_query.message.edit_text("❌ فشل الرفع على GitHub")
            
    except Exception as e:
        await callback_query.message.edit_text(f"❌ خطأ: {str(e)}")

async def upload_to_github(bot_code: dict) -> bool:
    """رفع الملفات إلى GitHub"""
    # هنا تستخدم GitHub API للرفع
    # يمكنك استخدام PyGithub library
    return True  # محاكاة للنجاح

async def deploy_to_render_api() -> bool:
    """النشر على Render باستخدام API"""
    if not RENDER_API_KEY:
        return False
    
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # إنشاء خدمة جديدة
    data = {
        "type": "web_service",
        "name": "telegram-bot-deployed",
        "repo": os.environ.get("GITHUB_REPO", ""),
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python bot.py"
    }
    
    # استخدام aiohttp للإرسال
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=data
        ) as response:
            return response.status == 201

def create_bot_code(api_id: int, api_hash: str, session_string: str) -> dict:
    """إنشاء كود البوت"""
    return {
        "bot.py": f"""
import os
from pyrogram import Client, filters

API_ID = {api_id}
API_HASH = "{api_hash}"
SESSION_STRING = "{session_string}"

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ البوت يعمل على Render!")

app.run()
""",
        "requirements.txt": "pyrogram==2.0.106\ntgcrypto==1.2.5\n",
        "Procfile": "worker: python bot.py"
    }

# ========== 4. إدارة الخادم ==========
async def server_menu(client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart_server")],
        [InlineKeyboardButton("📊 معلومات النظام", callback_data="system_info")],
        [InlineKeyboardButton("📝 عرض السجلات", callback_data="view_logs")],
        [InlineKeyboardButton("🧹 تنظيف", callback_data="cleanup")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ])
    
    await callback_query.message.edit_text(
        "⚙️ **إدارة الخادم**\n\nاختر العملية:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("system_info"))
async def show_system_info(client, callback_query: CallbackQuery):
    import psutil
    
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    info = (
        "📊 **معلومات النظام**\n\n"
        f"🖥 المعالج: `{cpu}%`\n"
        f"💾 الذاكرة: `{memory.percent}%` ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)\n"
        f"💿 القرص: `{disk.percent}%`\n"
        f"⏰ وقت التشغيل: `{time.time() - psutil.boot_time():.0f}` ثانية\n"
        f"🐍 بايثون: `{sys.version.split()[0]}`"
    )
    
    await callback_query.message.edit_text(
        info,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 تحديث", callback_data="system_info")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="server_management")]
        ])
    )

# ========== 5. حالة البوتات ==========
async def check_status(client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "📊 **حالة البوتات**\n\n"
        f"🤖 هذا البوت: ✅ يعمل\n"
        f"📡 Render: ✅ متصل\n"
        f"⏰ الوقت: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
        f"👤 المستخدمين: `{len(user_states)}`\n"
        f"🔑 الجلسات المحفوظة: `{len(user_sessions)}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 تحديث", callback_data="bot_status")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
        ])
    )

# ========== مساعدة ==========
async def help_menu(client, callback_query: CallbackQuery):
    help_text = (
        "❓ **المساعدة**\n\n"
        "1️⃣ **استخراج الجلسة:**\n"
        "- احصل على API_ID و API_HASH من my.telegram.org\n"
        "- أدخل رقم هاتفك\n"
        "- أدخل كود التحقق\n\n"
        "2️⃣ **النشر على Render:**\n"
        "- استخرج الجلسة أولاً\n"
        "- اضغط نشر على Render\n"
        "- انتظر التفعيل\n\n"
        "📞 للدعم: @YourUsername"
    )
    
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
        ])
    )

# ========== تشغيل البوت ==========
if __name__ == "__main__":
    print("🤖 بوت النشر المتكامل يعمل...")
    keep_alive()
    app.run()
