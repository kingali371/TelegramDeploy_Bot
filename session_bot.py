import asyncio
from pyrogram import Client
from typing import Tuple, Optional

class SessionExtractor:
    """فئة متقدمة لاستخراج الجلسات"""
    
    def __init__(self):
        self.active_sessions = {}
    
    async def extract_user_session(
        self,
        api_id: int,
        api_hash: str,
        phone_number: str
    ) -> Tuple[bool, str]:
        """
        استخراج جلسة مستخدم
        Returns: (success, session_string or error_message)
        """
        try:
            client = Client(
                f"session_{phone_number[-4:]}",
                api_id=api_id,
                api_hash=api_hash,
                in_memory=True
            )
            
            await client.connect()
            
            # إرسال كود التحقق
            sent_code = await client.send_code(phone_number)
            
            return True, {
                "phone_code_hash": sent_code.phone_code_hash,
                "client": client
            }
            
        except Exception as e:
            return False, str(e)
    
    async def verify_code(
        self,
        client: Client,
        phone_number: str,
        phone_code_hash: str,
        code: str
    ) -> Tuple[bool, str]:
        """التحقق من الكود واستخراج الجلسة"""
        try:
            await client.sign_in(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=code
            )
            
            session_string = await client.export_session_string()
            
            await client.disconnect()
            
            return True, session_string
            
        except Exception as e:
            return False, str(e)
    
    async def extract_bot_session(
        self,
        api_id: int,
        api_hash: str,
        bot_token: str
    ) -> Tuple[bool, str]:
        """استخراج جلسة بوت"""
        try:
            client = Client(
                f"bot_session_{bot_token[:8]}",
                api_id=api_id,
                api_hash=api_hash,
                bot_token=bot_token,
                in_memory=True
            )
            
            await client.connect()
            
            session_string = await client.export_session_string()
            
            await client.disconnect()
            
            return True, session_string
            
        except Exception as e:
            return False, str(e)
