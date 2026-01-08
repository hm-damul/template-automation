"""Multi-Language Support Module - 5 Languages with AI Translation"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Language(Enum):
    """지원 언어"""
    ENGLISH = ("en", "English", "영어", "$")
    SPANISH = ("es", "Spanish", "스페인어", "€")
    PORTUGUESE = ("pt", "Portuguese", "포르투갈어", "R$")
    JAPANESE = ("ja", "Japanese", "일본어", "¥")
    GERMAN = ("de", "German", "독일어", "€")
    KOREAN = ("ko", "Korean", "한국어", "₩")


class TranslationEngine:
    """AI 번역 엔진 - 무료 API 활용"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.cache_file = "translations_cache.json"
        self.load_cache()
    
    def load_cache(self):
        """번역 캐시 로드"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}
        else:
            self.cache = {}
    
    def save_cache(self):
        """번역 캐시 저장"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def translate_text(self, text: str, target_lang: Language, source_lang: Language = Language.ENGLISH) -> str:
        """텍스트 번역 - 무료 대안 포함"""
        if not text or text.strip() == "":
            return text
        
        cache_key = f"{source_lang.value[0]}_{target_lang.value[0]}_{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        translated = text
        
        try:
            if hasattr(self, 'openai_key') and self.openai_key:
                try:
                    import openai
                    client = openai.Client(api_key=self.openai_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"Translate from {source_lang.value[1]} to {target_lang.value[1]}. Only return translated text."},
                            {"role": "user", "content": text}
                        ],
                        max_tokens=2000,
                        temperature=0.3
                    )
                    
                    if response.choices:
                        choice = response.choices[0]
                        if choice.message and choice.message.content:
                            translated = choice.message.content.strip()
                    
                except Exception as openai_error:
                    if "quota" in str(openai_error).lower() or "429" in str(openai_error):
                        logger.warning("⚠️ OpenAI quota exceeded, using free translation...")
                    else:
                        raise
            
            # 무료 대안 사용
            if translated == text:
                translated = self._translate_google_free(text, source_lang, target_lang)
            
            self.cache[cache_key] = translated
            self.save_cache()
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def translate_template_content(self, content: Dict, target_langs: List[Language]) -> Dict:
        """템플릿 콘텐츠 다국어 번역"""
        translated_content = {
            "original": content,
            "translations": {}
        }
        
        for lang in target_langs:
            if lang == Language.ENGLISH:
                translated_content["translations"][lang.value[0]] = content
                continue
            
            lang_content = {}
            
            # 각 필드 번역
            fields_to_translate = [
                "name", "description", "full_description", 
                "marketing_copy", "usage_guide"
            ]
            
            for field in fields_to_translate:
                if field in content:
                    original_text = str(content[field])
                    if len(original_text) > 10:  # 10자 이상만 번역
                        translated = self.translate_text(
                            original_text, 
                            lang,
                            Language.ENGLISH
                        )
                    else:
                        translated = original_text
                    
                    lang_content[field] = translated
            
            # SEO 키워드 번역
            if "seo_keywords" in content:
                translated_keywords = []
                for keyword in content["seo_keywords"]:
                    translated_kw = self.translate_text(keyword, lang, Language.ENGLISH)
                    translated_keywords.append(translated_kw)
                lang_content["seo_keywords"] = translated_keywords
            
            # 태그 번역
            if "tags" in content:
                translated_tags = []
                for tag in content["tags"]:
                    translated_tag = self.translate_text(tag, lang, Language.ENGLISH)
                    translated_tags.append(translated_tag)
                lang_content["tags"] = translated_tags
            
            # 메타데이터 추가
            lang_content["language"] = lang.value[0]
            lang_content["language_name"] = lang.value[1]
            lang_content["translated_at"] = datetime.now().isoformat()
            
            translated_content["translations"][lang.value[0]] = lang_content
        
        return translated_content
    
    def generate_seo_metadata(self, template_data: Dict, lang: Language) -> Dict:
        """SEO 메타데이터 생성"""
        base_keywords = template_data.get("seo_keywords", [])
        
        # 언어별 SEO 키워드 확장
        seo_expansions = {
            Language.ENGLISH: ["template", "download", "digital"],
            Language.SPANISH: ["plantilla", "descargar", "digital"],
            Language.PORTUGUESE: ["modelo", "baixar", "digital"],
            Language.JAPANESE: ["テンプレート", "ダウンロード", "デジタル"],
            Language.GERMAN: ["vorlage", "herunterladen", "digital"]
        }
        
        expanded_keywords = base_keywords + seo_expansions.get(lang, [])
        
        return {
            "meta_title": f"{template_data['name']} - {lang.value[1]} Template",
            "meta_description": self.translate_text(
                template_data.get("description", "")[:160], 
                lang
            ),
            "keywords": expanded_keywords,
            "language": lang.value[0],
            "hreflang": self.generate_hreflang(template_data.get("slug", "")),
            "canonical_url": f"https://yoursite.com/templates/{template_data.get('slug', '')}"
        }
    
    def generate_hreflang(self, slug: str) -> Dict:
        """hreflang 태그 생성"""
        hreflang = {}
        
        for lang in Language:
            if lang == Language.KOREAN:  # 한국어는 제외 (모국어)
                continue
            hreflang[lang.value[0]] = f"https://yoursite.com/{lang.value[0]}/templates/{slug}"
        
        return hreflang


class MultiLanguageContentManager:
    """다국어 콘텐츠 관리자"""
    
    def __init__(self):
        self.translator = TranslationEngine()
        self.supported_languages = [
            Language.ENGLISH,
            Language.SPANISH,
            Language.PORTUGUESE,
            Language.JAPANESE,
            Language.GERMAN
        ]
    
    def create_multilingual_template(self, original_template: Dict) -> Dict:
        """다국어 템플릿 생성"""
        logger.info(f"Creating multilingual template: {original_template.get('name')}")
        
        # 번역 생성
        translated_content = self.translator.translate_template_content(
            original_template,
            self.supported_languages
        )
        
        # SEO 메타데이터 생성
        seo_metadata = {}
        for lang in self.supported_languages:
            seo_metadata[lang.value[0]] = self.translator.generate_seo_metadata(
                original_template, 
                lang
            )
        
        return {
            "template_id": original_template.get("id"),
            "original": original_template,
            "translations": translated_content["translations"],
            "seo_metadata": seo_metadata,
            "supported_languages": [lang.value[0] for lang in self.supported_languages],
            "created_at": datetime.now().isoformat()
        }
    
    def get_localized_product_data(self, template_id: str, language: str) -> Dict:
        """언어별 제품 데이터 반환"""
        # 실제로는 데이터베이스에서 조회
        return {
            "template_id": template_id,
            "language": language,
            "name": f"[{language.upper()}] Template Name",
            "description": "Localized description...",
            "price": self.get_localized_price(language),
            "currency": self.get_currency_symbol(language),
            "seo": {}
        }
    
    def get_currency_symbol(self, language: str) -> str:
        """통화 기호 반환"""
        for lang in Language:
            if lang.value[0] == language:
                return lang.value[3]
        return "$"
    
    def get_localized_price(self, language: str, base_usd: float = 49) -> float:
        """지역별 가격 최적화"""
        # 구매력 기반 가격 조정
        price_adjustments = {
            "en": 1.0,      # 미국 - 기본가
            "es": 0.85,     # 스페인 - 15% 할인
            "pt": 0.80,     # 브라질 - 20% 할인
            "ja": 0.90,     # 일본 - 10% 할인
            "de": 1.0       # 독일 - 기본가
        }
        
        adjustment = price_adjustments.get(language, 1.0)
        return round(base_usd * adjustment, 2)
    
    def generate_language_report(self) -> Dict:
        """언어별 성과 리포트"""
        return {
            "english": {
                "templates": 50,
                "revenue": 2500,
                "conversion_rate": 3.2,
                "avg_order_value": 45
            },
            "spanish": {
                "templates": 30,
                "revenue": 1200,
                "conversion_rate": 2.8,
                "avg_order_value": 38
            },
            "portuguese": {
                "templates": 25,
                "revenue": 900,
                "conversion_rate": 2.5,
                "avg_order_value": 36
            },
            "japanese": {
                "templates": 20,
                "revenue": 1100,
                "conversion_rate": 2.9,
                "avg_order_value": 55
            },
            "german": {
                "templates": 15,
                "revenue": 800,
                "conversion_rate": 2.6,
                "avg_order_value": 48
            }
        }


# Export
translation_engine = TranslationEngine()
multilingual_manager = MultiLanguageContentManager()
