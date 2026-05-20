import os
import aiohttp
import json
from typing import Dict, Optional

class RenderDeployer:
    """فئة للنشر على Render"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_service(
        self,
        name: str,
        repo_url: str,
        env_vars: Dict[str, str]
    ) -> Optional[str]:
        """إنشاء خدمة جديدة على Render"""
        
        data = {
            "type": "web_service",
            "name": name,
            "repo": repo_url,
            "branch": "main",
            "env": "python",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "python bot.py",
            "envVars": [
                {"key": k, "value": v}
                for k, v in env_vars.items()
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/services",
                headers=self.headers,
                json=data
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    return result.get("id")
                return None
    
    async def restart_service(self, service_id: str) -> bool:
        """إعادة تشغيل خدمة"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/services/{service_id}/restart",
                headers=self.headers
            ) as response:
                return response.status == 200
    
    async def delete_service(self, service_id: str) -> bool:
        """حذف خدمة"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/services/{service_id}",
                headers=self.headers
            ) as response:
                return response.status == 204
    
    async def get_service_status(self, service_id: str) -> Optional[Dict]:
        """جلب حالة الخدمة"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/services/{service_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
