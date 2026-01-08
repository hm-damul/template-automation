"""Platform Automation Module - Gumroad Integration"""
import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GumroadAPI:
    """Gumroad 플랫폼 자동화"""
    
    BASE_URL = "https://api.gumroad.com/v2"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GUMROAD_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_product(self, product_data: Dict) -> Dict:
        """제품 생성 (템플릿 등록)"""
        endpoint = f"{self.BASE_URL}/products"
        
        payload = {
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "price": product_data.get("price", 0),
            "currency": product_data.get("currency", "USD"),
            "custom_permalink": product_data.get("permalink", ""),
            "tags": product_data.get("tags", []),
            "template_id": product_data.get("template_id", ""),
            "featured": product_data.get("featured", False),
            "max_purchase_count": product_data.get("max_purchase_count", 0),
            "variants": product_data.get("variants", [])
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Product created on Gumroad: {result.get('product', {}).get('name')}")
            
            return {
                "success": True,
                "product_id": result.get("product", {}).get("id"),
                "url": result.get("product", {}).get("url"),
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error creating Gumroad product: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_file(self, product_id: str, file_path: str) -> Dict:
        """제품 파일 업로드"""
        endpoint = f"{self.BASE_URL}/products/{product_id}/upload"
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(
                    endpoint, 
                    files=files,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                
                return {"success": True, "data": response.json()}
                
        except Exception as e:
            logger.error(f"Error uploading file to Gumroad: {e}")
            return {"success": False, "error": str(e)}
    
    def get_products(self, page: int = 1, limit: int = 100) -> Dict:
        """제품 목록 조회"""
        endpoint = f"{self.BASE_URL}/products"
        params = {"page": page, "limit": limit}
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Gumroad products: {e}")
            return {"success": False, "error": str(e)}
    
    def update_product(self, product_id: str, update_data: Dict) -> Dict:
        """제품 업데이트"""
        endpoint = f"{self.BASE_URL}/products/{product_id}"
        
        try:
            response = requests.put(endpoint, json=update_data, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error updating Gumroad product: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_product(self, product_id: str) -> Dict:
        """제품 삭제"""
        endpoint = f"{self.BASE_URL}/products/{product_id}"
        
        try:
            response = requests.delete(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error deleting Gumroad product: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sales(self, start_date: str = None, end_date: str = None) -> Dict:
        """매출 조회"""
        endpoint = f"{self.BASE_URL}/sales"
        params = {}
        
        if start_date:
            params["started_after"] = start_date
        if end_date:
            params["started_before"] = end_date
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Gumroad sales: {e}")
            return {"success": False, "error": str(e)}
    
    def get_earnings(self) -> Dict:
        """수익 조회"""
        endpoint = f"{self.BASE_URL}/earnings"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Gumroad earnings: {e}")
            return {"success": False, "error": str(e)}
    
    def create_subscription(self, product_id: str, subscription_data: Dict) -> Dict:
        """구독 제품 생성"""
        endpoint = f"{self.BASE_URL}/products"
        
        payload = {
            "name": subscription_data.get("name"),
            "description": subscription_data.get("description"),
            "price": subscription_data.get("price", 0),
            "currency": "USD",
            "recurring": True,
            "interval": subscription_data.get("interval", "month"),
            "template_id": subscription_data.get("template_id", ""),
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {"success": False, "error": str(e)}
    
    def get_webhook_subscriptions(self) -> List[Dict]:
        """웹훅 구독 목록 조회"""
        endpoint = f"{self.BASE_URL}/webhook_subscriptions"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return response.json().get("webhook_subscriptions", [])
            
        except Exception as e:
            logger.error(f"Error getting webhook subscriptions: {e}")
            return []
    
    def register_webhook(self, url: str, events: List[str]) -> Dict:
        """웹훅 등록"""
        endpoint = f"{self.BASE_URL}/webhook_subscriptions"
        
        payload = {
            "url": url,
            "events": events
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            return {"success": False, "error": str(e)}


class GumroadAutomation:
    """Gumroad 자동화 오케스트레이터"""
    
    def __init__(self, api_key: str = None):
        self.api = GumroadAPI(api_key)
        self.daily_published_count = 0
        
    def publish_template(self, template_data: Dict, file_path: str = None) -> Dict:
        """템플릿 자동 게시"""
        logger.info(f"Publishing template to Gumroad: {template_data.get('name')}")
        
        # 1. 제품 생성
        product_result = self.api.create_product(template_data)
        
        if not product_result.get("success"):
            return product_result
        
        # 2. 파일 업로드 (있는 경우)
        if file_path:
            upload_result = self.api.upload_file(
                product_result["product_id"], 
                file_path
            )
            if not upload_result.get("success"):
                logger.warning(f"File upload failed: {upload_result.get('error')}")
        
        self.daily_published_count += 1
        
        return {
            "success": True,
            "product_id": product_result.get("product_id"),
            "url": product_result.get("url"),
            "platform": "gumroad"
        }
    
    def get_daily_publish_count(self) -> int:
        """오늘 게시한 템플릿 수 반환"""
        return self.daily_published_count
    
    def can_publish_more(self, platform: str = "gumroad") -> bool:
        """더 게시할 수 있는지 확인"""
        from ..core.config import PlatformLimits
        
        max_daily = PlatformLimits.get_random_daily_count(platform)
        return self.daily_published_count < max_daily
    
    def get_performance_stats(self) -> Dict:
        """성능 통계 조회"""
        sales = self.api.get_sales()
        earnings = self.api.get_earnings()
        
        return {
            "total_sales": len(sales.get("sales", [])),
            "total_revenue": earnings.get("available", 0),
            "currency": earnings.get("currency", "USD"),
            "published_today": self.daily_published_count
        }


# Export
gumroad_api = GumroadAPI()
gumroad_automation = GumroadAutomation()
