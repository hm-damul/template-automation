"""Additional Platforms Module - Etsy, Payhip Integration"""
import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EtsyAPI:
    """Etsy 플랫폼 자동화"""
    
    BASE_URL = "https://openapi.etsy.com/v3"
    
    def __init__(self):
        self.api_key = os.getenv("ETSY_API_KEY")
        self.client_id = os.getenv("ETSY_CLIENT_ID")
        self.client_secret = os.getenv("ETSY_CLIENT_SECRET")
        self.shop_id = os.getenv("ETSY_SHOP_ID")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "x-api-key": self.client_id
        }
    
    def create_listing(self, listing_data: Dict) -> Dict:
        """Etsy 리스팅 생성"""
        endpoint = f"{self.BASE_URL}/applications/listings"
        
        payload = {
            "quantity": 1,
            "title": listing_data.get("title", "")[:140],
            "description": listing_data.get("description", ""),
            "price": listing_data.get("price", 0),
            "currency_code": "USD",
            "taxonomy_id": listing_data.get("taxonomy_id", 66),  # Digital Downloads
            "materials": listing_data.get("materials", []),
            "tags": listing_data.get("tags", [])[:13],  # Max 13 tags
            "who_made": "i_did",
            "when_made": "2020_2024",
            "is_supply": True,
            "processing_time": "1-3 days",
            "style": listing_data.get("style", [])
        }
        
        try:
            response = requests.post(
                endpoint, 
                json=payload, 
                headers=self.headers
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Etsy listing created: {result.get('listing_id')}")
            
            return {
                "success": True,
                "listing_id": result.get("listing_id"),
                "url": f"https://www.etsy.com/listing/{result.get('listing_id')}",
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Etsy listing error: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_listing_images(self, listing_id: str, image_urls: List[str]) -> Dict:
        """리스팅 이미지 업로드"""
        endpoint = f"{self.BASE_URL}/applications/listings/{listing_id}/images"
        
        images = []
        for i, url in enumerate(image_urls[:10]):  # Max 10 images
            try:
                response = requests.post(
                    endpoint,
                    json={"url": url, "rank": i + 1},
                    headers=self.headers
                )
                response.raise_for_status()
                images.append(response.json())
            except Exception as e:
                logger.error(f"Etsy image upload error: {e}")
        
        return {"success": True, "images_uploaded": len(images)}
    
    def get_listings(self, status: str = "active") -> Dict:
        """리스팅 목록 조회"""
        endpoint = f"{self.BASE_URL}/applications/shops/{self.shop_id}/listings"
        
        try:
            response = requests.get(
                endpoint,
                params={"status": status, "limit": 100},
                headers=self.headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Etsy listings error: {e}")
            return {"success": False, "error": str(e)}
    
    def update_inventory(self, listing_id: str, inventory: Dict) -> Dict:
        """재고 업데이트"""
        endpoint = f"{self.BASE_URL}/applications/listings/{listing_id}/inventory"
        
        payload = {
            "products": [{
                "sku": inventory.get("sku", ""),
                "quantity": 9999,  # Digital products
                "is_customizable": True,
                "personalizations": {
                    "character_limit": 500,
                    "included_text": ["Your name", "Custom details"]
                }
            }]
        }
        
        try:
            response = requests.put(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {"success": True, "data": response.json()}
            
        except Exception as e:
            logger.error(f"Etsy inventory error: {e}")
            return {"success": False, "error": str(e)}


class PayhipAPI:
    """Payhip 플랫폼 자동화"""
    
    BASE_URL = "https://api.payhip.com/v1"
    
    def __init__(self):
        self.api_key = os.getenv("PAYHIP_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_product(self, product_data: Dict) -> Dict:
        """Payhip 제품 생성"""
        endpoint = f"{self.BASE_URL}/product"
        
        payload = {
            "name": product_data.get("name"),
            "desc": product_data.get("description", ""),
            "price": product_data.get("price", 0),
            "type": "digital",  # Digital product
            "file_url": product_data.get("file_url", ""),
            "preview_url": product_data.get("preview_url", ""),
            "variants": product_data.get("variants", []),
            "options": product_data.get("options", {
                "pay_what_you_want": False,
                "bundles": True,
                "affiliates": True
            })
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Payhip product created: {result.get('id')}")
            
            return {
                "success": True,
                "product_id": result.get("id"),
                "url": result.get("url"),
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Payhip product error: {e}")
            return {"success": False, "error": str(e)}
    
    def create_link(self, product_id: str, link_data: Dict) -> Dict:
        """유료 링크 생성 (개인화 결제 링크)"""
        endpoint = f"{self.BASE_URL}/link"
        
        payload = {
            "product_id": product_id,
            "custom_price": link_data.get("custom_price", 0),
            "custom_fields": link_data.get("custom_fields", {}),
            "expire_at": link_data.get("expire_at", ""),
            "max_count": link_data.get("max_count", 1)
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return {
                "success": True,
                "link_id": response.json().get("id"),
                "url": response.json().get("url")
            }
            
        except Exception as e:
            logger.error(f"Payhip link error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sales(self, start_date: str = None, end_date: str = None) -> Dict:
        """매출 조회"""
        endpoint = f"{self.BASE_URL}/sales"
        params = {}
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Payhip sales error: {e}")
            return {"success": False, "error": str(e)}


class PlatformExpansionManager:
    """플랫폼 확장 관리자"""
    
    def __init__(self):
        self.etsy = EtsyAPI()
        self.payhip = PayhipAPI()
        self.gumroad = None  # 기존 Gumroad 모듈
        self.lemon_squeezy = None  # 기존 Lemon Squeezy 모듈
        
        # 플랫폼별 최적화 설정
        self.platform_configs = {
            "gumroad": {
                "max_daily": 10,
                "optimal_price_range": (8, 149),
                "digital_focus": True,
                "crypto_support": False
            },
            "etsy": {
                "max_daily": 5,
                "optimal_price_range": (5, 100),
                "digital_focus": True,
                "search_based": True,
                "tags_required": True
            },
            "payhip": {
                "max_daily": 15,
                "optimal_price_range": (10, 99),
                "digital_focus": True,
                "affiliate_system": True
            },
            "lemon_squeezy": {
                "max_daily": 10,
                "optimal_price_range": (15, 199),
                "tax_included": True,
                "subscription_support": True
            }
        }
    
    def distribute_template(self, template_data: Dict) -> Dict:
        """템플릿을 최적의 플랫폼에 배포"""
        results = {
            "template_id": template_data.get("id"),
            "name": template_data.get("name"),
            "price": template_data.get("price"),
            "deployments": []
        }
        
        price = template_data.get("price", 49)
        
        # 가격대별 최적 플랫폼 결정
        if price <= 19:
            # 저가: Etsy + Payhip
            platforms = ["etsy", "payhip"]
        elif price <= 79:
            # 중가: Gumroad + Payhip + Etsy
            platforms = ["gumroad", "payhip"]
        else:
            # 고가: Gumroad + Lemon Squeezy
            platforms = ["gumroad", "lemon_squeezy"]
        
        for platform in platforms:
            config = self.platform_configs.get(platform)
            if not config:
                continue
            
            # 플랫폼별 데이터 변환
            platform_data = self._adapt_for_platform(template_data, platform)
            
            # 배포 실행
            if platform == "etsy":
                result = self.etsy.create_listing(platform_data)
            elif platform == "payhip":
                result = self.payhip.create_product(platform_data)
            elif platform == "gumroad" and self.gumroad:
                result = self.gumroad.publish_template(platform_data)
            elif platform == "lemon_squeezy" and self.lemon_squeezy:
                result = self.lemon_squeezy.publish_template(platform_data)
            else:
                continue
            
            if result.get("success"):
                results["deployments"].append({
                    "platform": platform,
                    "url": result.get("url") or result.get("buy_url"),
                    "product_id": result.get("product_id") or result.get("listing_id")
                })
        
        logger.info(f"Template distributed to {len(results['deployments'])} platforms")
        
        return results
    
    def _adapt_for_platform(self, template_data: Dict, platform: str) -> Dict:
        """플랫폼별 데이터 변환"""
        adapted = {
            "name": template_data.get("name", "")[:platform.get("max_title_length", 140)],
            "description": template_data.get("description", ""),
            "price": template_data.get("price", 0),
            "tags": template_data.get("tags", [])[:13] if platform == "etsy" else template_data.get("tags", []),
            "file_url": template_data.get("file_url", ""),
            "preview_url": template_data.get("preview_url", "")
        }
        
        if platform == "etsy":
            adapted["taxonomy_id"] = 66  # Digital Downloads
            adapted["materials"] = ["Digital", "Downloadable", "Template"]
            adapted["style"] = ["Modern", "Professional"]
        
        elif platform == "payhip":
            adapted["variants"] = [
                {"name": "Basic", "price": template_data.get("price", 0)},
                {"name": "Premium", "price": template_data.get("price", 0) * 1.5}
            ]
        
        return adapted
    
    def get_platform_comparison(self) -> Dict:
        """플랫폼 비교 분석"""
        return {
            "gumroad": {
                "fees": "10% + $0.50",
                "pros": ["간편", "다양한 결제", "대형 커뮤니티"],
                "cons": ["높은 수수료", "제한적 커스터마이징"],
                "best_for": "일반 디지털 제품"
            },
            "etsy": {
                "fees": "6.5% + $0.20/listing",
                "pros": ["대형 마켓플레이스", "SEO 유리", "국제 노출"],
                "cons": ["경쟁 심함", "신규 셀러 제한"],
                "best_for": "디자인 중심 제품"
            },
            "payhip": {
                "fees": "5% (무료플랜)",
                "pros": ["저렴", "간편", "제휴 시스템"],
                "cons": ["소규모 마켓플레이스", "제한적 분석"],
                "best_for": "간편한 디지털 판매"
            },
            "lemon_squeezy": {
                "fees": "5% + $0.50",
                "pros": ["세금 자동 처리", "구독 지원", "다양한 통화"],
                "cons": ["상대적으로 신규", "미국 중심"],
                "best_for": "국제 판매"
            }
        }


# Export
platform_expansion = PlatformExpansionManager()
