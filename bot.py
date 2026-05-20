from flask import Flask
from threading import Thread
import os

# خادم وهمي لمنع Render من إيقاف البوت
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "البوت يعمل ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# في بداية الملف
if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # تشغيل البوت
    print("🚀 جاري تشغيل البوت...")
    app.run()
