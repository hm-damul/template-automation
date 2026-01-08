"""Platform Automation Module - Lemon Squeezy Integration"""
import os
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LemonSqueezyAPI:
    """Lemon Squeezy 플랫폼 자동화 - MoR (Merchant of Record) 세금 처리"""
    
    BASE_URL = "https://api.lemonsqueezy.com/v1"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("LEMON_SQUEEZY_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        }
    
    def create_product(self, product_data: Dict) -> Dict:
        """제품 생성 (템플릿 등록)"""
        endpoint = f"{self.BASE_URL}/products"
        
        payload = {
            "data": {
                "type": "products",
                "attributes": {
                    "name": product_data.get("name"),
                    "description": product_data.get("description"),
                    "price": product_data.get("price", 0),
                    "currency": "USD",
                    "buy_url": product_data.get("buy_url", ""),
                    "file_path": product_data.get("file_path", ""),
                    "preview_url": product_data.get("preview_url", ""),
                    "large_preview_url": product_data.get("large_preview_url", ""),
                    "template_id": product_data.get("template_id", ""),
                    "status": "published"
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": product_data.get("store_id", "")
                        }
                    },
                    "variants": {
                        "data": [
                            {
                                "type": "variants",
                                "attributes": {
                                    "name": "Default",
                                    "price": product_data.get("price", 0),
                                    "is_primary": True
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Product created on Lemon Squeezy: {result['data']['attributes']['name']}")
            
            return {
                "success": True,
                "product_id": result['data']['id'],
                "buy_url": result['data']['attributes']['buy_url'],
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Error creating Lemon Squeezy product: {e}")
            return {"success": False, "error": str(e)}
    
    def create_variant(self, product_id: str, variant_data: Dict) -> Dict:
        """변형(가격 옵션) 생성"""
        endpoint = f"{self.BASE_URL}/variants"
        
        payload = {
            "data": {
                "type": "variants",
                "attributes": {
                    "name": variant_data.get("name", "Default"),
                    "price": variant_data.get("price", 0),
                    "is_primary": variant_data.get("is_primary", True),
                    "pay_what_you_want": variant_data.get("pay_what_you_want", False)
                },
                "relationships": {
                    "product": {
                        "data": {
                            "type": "products",
                            "id": product_id
                        }
                    }
                }
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error creating variant: {e}")
            return {"success": False, "error": str(e)}
    
    def get_products(self, store_id: str = None, page: int = 1) -> Dict:
        """제품 목록 조회"""
        endpoint = f"{self.BASE_URL}/products"
        params = {"page": page}
        
        if store_id:
            params["filter[store]"] = store_id
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Lemon Squeezy products: {e}")
            return {"success": False, "error": str(e)}
    
    def update_product(self, product_id: str, update_data: Dict) -> Dict:
        """제품 업데이트"""
        endpoint = f"{self.BASE_URL}/products/{product_id}"
        
        payload = {
            "data": {
                "id": product_id,
                "type": "products",
                "attributes": update_data
            }
        }
        
        try:
            response = requests.patch(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error updating Lemon Squeezy product: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_product(self, product_id: str) -> Dict:
        """제품 삭제"""
        endpoint = f"{self.BASE_URL}/products/{product_id}"
        
        try:
            response = requests.delete(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error deleting Lemon Squeezy product: {e}")
            return {"success": False, "error": str(e)}
    
    def get_orders(self, store_id: str = None, status: str = None) -> Dict:
        """주문 목록 조회"""
        endpoint = f"{self.BASE_URL}/orders"
        params = {"page": 1}
        
        if store_id:
            params["filter[store]"] = store_id
        if status:
            params["filter[status]"] = status
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return {"success": False, "error": str(e)}
    
    def get_order(self, order_id: str) -> Dict:
        """특정 주문 조회"""
        endpoint = f"{self.BASE_URL}/orders/{order_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return {"success": False, "error": str(e)}
    
    def create_subscription(self, variant_id: str, subscription_data: Dict) -> Dict:
        """구독 생성"""
        endpoint = f"{self.BASE_URL}/subscriptions"
        
        payload = {
            "data": {
                "type": "subscriptions",
                "attributes": {
                    "variant_id": variant_id,
                    "customer_id": subscription_data.get("customer_id", ""),
                    "billing_cycle": subscription_data.get("billing_cycle", "month"),
                    "urls": {
                        "success_url": subscription_data.get("success_url", ""),
                        "cancel_url": subscription_data.get("cancel_url", "")
                    }
                }
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {"success": False, "error": str(e)}
    
    def get_license_keys(self, order_id: str = None) -> Dict:
        """라이선스 키 조회"""
        endpoint = f"{self.BASE_URL}/license-keys"
        params = {}
        
        if order_id:
            params["filter[order]"] = order_id
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting license keys: {e}")
            return {"success": False, "error": str(e)}
    
    def create_webhook(self, webhook_data: Dict) -> Dict:
        """웹훅 생성"""
        endpoint = f"{self.BASE_URL}/webhooks"
        
        payload = {
            "data": {
                "type": "webhooks",
                "attributes": {
                    "name": webhook_data.get("name", "Template Automation"),
                    "url": webhook_data.get("url", ""),
                    "event": webhook_data.get("events", []),
                    "secret": webhook_data.get("secret", "")
                }
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stores(self) -> Dict:
        """스토어 목록 조회"""
        endpoint = f"{self.BASE_URL}/stores"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting stores: {e}")
            return {"success": False, "error": str(e)}


class LemonSqueezyAutomation:
    """Lemon Squeezy 자동화 오케스트레이터"""
    
    def __init__(self, api_key: str = None):
        self.api = LemonSqueezyAPI(api_key)
        self.daily_published_count = 0
        self.store_id = None
        
    def initialize_store(self) -> bool:
        """스토어 초기화"""
        stores = self.api.get_stores()
        
        if stores.get("data"):
            self.store_id = stores["data"][0]["id"]
            logger.info(f"Using Lemon Squeezy store: {self.store_id}")
            return True
        
        logger.error("No Lemon Squeezy store found")
        return False
    
    def publish_template(self, template_data: Dict, file_path: str = None) -> Dict:
        """템플릿 자동 게시"""
        if not self.store_id:
            if not self.initialize_store():
                return {"success": False, "error": "Store not initialized"}
        
        logger.info(f"Publishing template to Lemon Squeezy: {template_data.get('name')}")
        
        # 제품 데이터 준비
        product_data = {
            "name": template_data.get("name"),
            "description": template_data.get("description"),
            "price": template_data.get("price", 0) * 100,  # cents로 변환
            "store_id": self.store_id,
            "template_id": template_data.get("template_id", ""),
            "file_path": file_path or ""
        }
        
        result = self.api.create_product(product_data)
        
        if result.get("success"):
            self.daily_published_count += 1
        
        return result
    
    def get_performance_stats(self) -> Dict:
        """성능 통계"""
        orders = self.api.get_orders()
        
        total_orders = len(orders.get("data", []))
        total_revenue = sum(
            order["attributes"]["total_formatted"]
            for order in orders.get("data", [])
        )
        
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "currency": "USD",
            "published_today": self.daily_published_count,
            "store_id": self.store_id
        }


# Export
lemon_squeezy_api = LemonSqueezyAPI()
lemon_squeezy_automation = LemonSqueezyAutomation()
