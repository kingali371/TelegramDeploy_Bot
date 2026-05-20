from flask import Flask, jsonify, request
from threading import Thread
import time
import requests
import random
import os

class KeepAlive:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.visit_count = 0
        self.start_time = time.time()
    
    def setup_routes(self):
        """إعداد المسارات"""
        
        @self.app.route('/')
        def home():
            self.visit_count += 1
            return jsonify({
                "status": "alive",
                "message": "البوت يعمل بقوة 💪",
                "uptime": int(time.time() - self.start_time),
                "visits": self.visit_count,
                "timestamp": time.time()
            })
        
        @self.app.route('/health')
        def health():
            return jsonify({"status": "healthy"}), 200
        
        @self.app.route('/ping')
        def ping():
            return jsonify({"response": "pong", "time": time.time()})
        
        @self.app.route('/stats')
        def stats():
            uptime = int(time.time() - self.start_time)
            return jsonify({
                "uptime_seconds": uptime,
                "uptime_formatted": f"{uptime//3600}h {(uptime%3600)//60}m",
                "visits": self.visit_count,
                "server": "Render",
                "python_version": "3.10+"
            })
    
    def self_ping(self):
        """نظام ping ذاتي لمنع النوم"""
        app_url = os.environ.get("RENDER_EXTERNAL_URL", "")
        if not app_url:
            print("⚠️ لم يتم العثور على URL الخدمة")
            return
        
        while True:
            try:
                # إرسال طلب كل 5-10 دقائق
                sleep_time = random.randint(300, 600)
                time.sleep(sleep_time)
                
                # طلب الصفحة الرئيسية
                requests.get(f"{app_url}/health", timeout=10)
                print(f"🔄 تم تجديد النشاط في {time.strftime('%H:%M:%S')}")
                
                # تناوب مع ping
                time.sleep(random.randint(60, 120))
                requests.get(f"{app_url}/ping", timeout=10)
                
            except Exception as e:
                print(f"⚠️ خطأ في التجديد الذاتي: {e}")
                time.sleep(30)
    
    def run(self):
        """تشغيل الخادم"""
        port = int(os.environ.get("PORT", 8080))
        
        # بدء الـ self-ping في Thread منفصل
        ping_thread = Thread(target=self.self_ping, daemon=True)
        ping_thread.start()
        
        print(f"🌐 الخادم يعمل على المنفذ {port}")
        self.app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    """وظيفة مساعدة"""
    server = KeepAlive()
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    print("🛡️ نظام الحماية من النوم نشط")
