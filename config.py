import os
from typing import Dict, Any

class Config:
    """إعدادات البوت المتقدمة"""
    
    # الإعدادات الأساسية
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    
    # إعدادات الأداء
    MAX_WORKERS = 100
    SLEEP_THRESHOLD = 60
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # إعدادات الأمان
    MAX_MESSAGE_LENGTH = 4096
    RATE_LIMIT = 20  # رسائل في الثانية
    
    # إعدادات التخزين
    SESSION_DIR = "./sessions"
    LOG_DIR = "./logs"
    
    # إعدادات Render
    PORT = int(os.environ.get("PORT", 8080))
    WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
    
    @classmethod
    def validate(cls) -> bool:
        """التحقق من الإعدادات"""
        required = [cls.API_ID, cls.API_HASH, cls.SESSION_STRING]
        return all(required)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """تحويل الإعدادات إلى قاموس"""
        return {
            key: value 
            for key, value in cls.__dict__.items() 
            if not key.startswith('_') and key.isupper()
        }
