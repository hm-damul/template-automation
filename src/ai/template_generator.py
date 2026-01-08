"""AI Template Generator - Core AI Engine for Autonomous Template Creation"""
# ✅ 반드시 최상위에 위치해야 함!
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드 (최초 1회만)
ENV_LOADED = False
try:
    PROJECT_ROOT = Path(__file__).parent.parent
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
        ENV_LOADED = True
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            print(f"✅ API Key loaded successfully: {api_key[:20]}...")
        else:
            print("⚠️ OPENAI_API_KEY not found in .env")
    else:
        print("⚠️ .env file not found")
except Exception as e:
    print(f"⚠️ Error loading .env: {e}")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Try to import AI libraries, handle gracefully if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic not available")


class TemplateType(Enum):
    NOTION = "notion"
    CANVA = "canva"
    PDF = "pdf"
    EXCEL = "excel"
    DIGITAL_PLANNER = "digital_planner"
    BUSINESS = "business"


class TemplateCategory(Enum):
    PRODUCTIVITY = "productivity"
    FINANCE = "finance"
    PLANNING = "planning"
    MARKETING = "marketing"
    EDUCATION = "education"
    CREATIVE = "creative"
    BUSINESS = "business"


class PricingTier(Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"
    BUNDLE_BASIC = "bundle_basic"
    BUNDLE_PREMIUM = "bundle_premium"
    BUNDLE_ALL_ACCESS = "bundle_all_access"


@dataclass
class TemplateSpec:
    """템플릿 스펙"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: TemplateType = TemplateType.NOTION
    category: TemplateCategory = TemplateCategory.PRODUCTIVITY
    description: str = ""
    features: List[str] = field(default_factory=list)
    target_audience: str = ""
    price_tier: PricingTier = PricingTier.MID
    estimated_price: float = 0.0
    bundle_products: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """트렌드 분석 결과"""
    niche: str
    trend_score: float
    competition_level: str
    growth_rate: float
    recommended_price_range: Tuple[float, float]
    top_performers: List[Dict]
    market_gap: List[str]
    recommendations: List[str]
    template_type: TemplateType = TemplateType.NOTION
    bundle_opportunities: List[str] = field(default_factory=list)


class TemplateAIGenerator:
    """AI 템플릿 생성기 - 핵심 자율 의사결정 엔진"""
    
    def __init__(self, openai_key: str = None, anthropic_key: str = None):
        self.openai_client = openai.Client(api_key=openai_key or os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = Anthropic(api_key=anthropic_key or os.getenv("ANTHROPIC_API_KEY"))
        
        self.successful_sellers = [
            {"name": "Thomas Frank", "revenue": "$2.1M/year", "strategy": "bundling, youtube"},
            {"name": "Easlo", "revenue": "$500K+/year", "strategy": "minimalism, premium"},
            {"name": "Optemization", "revenue": "$1M ARR", "strategy": "consulting + templates"}
        ]
        
        self.trending_niches = []
        self.generated_templates = []
        
    def analyze_trends_and_decide(self, market_data: List[Dict]) -> TrendAnalysis:
        """트렌드 분석 후 자율 결정"""
        logger.info("Analyzing market trends for template decisions...")
        
        prompt = f"""
You are an expert template business analyst. Analyze the following market data and make autonomous decisions:

Market Data: {json.dumps(market_data, indent=2)}

Successful Sellers Strategy:
{json.dumps(self.successful_sellers, indent=2)}

Based on this analysis, decide:
1. Best niche to enter (highest opportunity with manageable competition)
2. Optimal template type for this niche
3. Target price point
4. Key features to include
5. Bundle opportunities

Return your decision as a JSON object with these fields:
- niche: chosen niche name
- trend_score: 0-1 score
- competition_level: low/medium/high
- growth_rate: percentage
- recommended_price_range: [min, max]
- top_performers: list of top 3 selling templates in this niche
- market_gap: 3 opportunities competitors are missing
- recommendations: 5 specific recommendations for template creation
- template_type: notion/canva/pdf/excel/digital_planner
- bundle_opportunities: list of potential bundle combinations
"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            
            return TrendAnalysis(
                niche=result.get("niche", "Productivity"),
                trend_score=result.get("trend_score", 0.7),
                competition_level=result.get("competition_level", "medium"),
                growth_rate=result.get("growth_rate", 0.15),
                recommended_price_range=tuple(result.get("recommended_price_range", [29, 79])),
                top_performers=result.get("top_performers", []),
                market_gap=result.get("market_gap", []),
                recommendations=result.get("recommendations", []),
                template_type=TemplateType(result.get("template_type", "notion")),
                bundle_opportunities=result.get("bundle_opportunities", [])
            )
            
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return self._fallback_trend_analysis()
    
    def generate_template_spec(self, analysis: TrendAnalysis) -> TemplateSpec:
        """트렌드 분석 기반으로 템플릿 스펙 자율 생성"""
        logger.info(f"Generating template spec for: {analysis.niche}")
        
        price = self._calculate_optimal_price(analysis)
        bundle_products = self._generate_bundle_decision(analysis)
        
        prompt = f"""
Create a detailed template specification for a {analysis.template_type.value} template in the {analysis.niche} niche.

Analysis Summary:
- Trend Score: {analysis.trend_score}
- Competition: {analysis.compliance_level}
- Growth Rate: {analysis.growth_rate * 100}%
- Market Gaps: {analysis.market_gap}

Based on successful seller strategies ({json.dumps(self.successful_sellers)}), create a template that:
1. Solves a specific problem clearly
2. Has unique differentiation from competitors
3. Includes all essential features for the niche
4. Is priced optimally at ${price}

Return JSON with:
- name: creative template name
- description: compelling description (150-200 chars)
- features: list of 5-7 key features
- target_audience: specific persona
- price_tier: low/mid/high/bundle_basic/bundle_premium/bundle_all_access
- estimated_price: number
- bundle_products: list of product IDs to bundle (empty if not a bundle)
"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            
            return TemplateSpec(
                name=result.get("name", f"{analysis.niche} Template"),
                type=analysis.template_type,
                category=self._categorize_niche(analysis.niche),
                description=result.get("description", ""),
                features=result.get("features", []),
                target_audience=result.get("target_audience", "Professionals"),
                price_tier=PricingTier(result.get("price_tier", "mid")),
                estimated_price=result.get("estimated_price", price),
                bundle_products=result.get("bundle_products", []),
                metadata={
                    "trend_analysis": asdict(analysis),
                    "strategy_source": "ai_autonomous"
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating template spec: {e}")
            return self._fallback_template_spec(analysis)
    
    def generate_template_content(self, spec: TemplateSpec) -> Dict:
        """템플릿 실제 콘텐츠 생성"""
        logger.info(f"Generating content for: {spec.name}")
        
        prompt = f"""
Create complete template content for:
Name: {spec.name}
Type: {spec.type.value}
Category: {spec.category.value}
Target: {spec.target_audience}

Features to include:
{json.dumps(spec.features, indent=2)}

Description:
{spec.description}

Return JSON with:
1. full_description: detailed description for product page
2. template_structure: hierarchical outline of the template
3. page_contents: detailed content for each section
4. usage_guide: step-by-step usage instructions
5. marketing_copy: persuasive marketing text
6. seo_keywords: relevant keywords for search optimization
"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Error generating template content: {e}")
            return self._fallback_content(spec)
    
    def create_design_prompt(self, spec: TemplateSpec) -> str:
        """디자인 생성용 프롬프트 (Canva/DALL-E용)"""
        prompt = f"""
Create a professional {spec.type.value} template design for {spec.category.value}.

Template Name: {spec.name}
Target Audience: {spec.target_audience}
Key Features:
{chr(10).join(f"- {f}" for f in spec.features[:5])}

Style Guidelines:
- Modern and clean aesthetic
- Professional color scheme suitable for {spec.target_audience}
- Clear visual hierarchy
- Easy to customize elements
- Placeholder text clearly indicated

Include:
- Header section with template name
- Navigation/table of contents if applicable
- Content sections matching features
- Call-to-action or footer area

Return only the prompt text, be specific and detailed.
"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return self._fallback_design_prompt(spec)
    
    def calculate_price(self, spec: TemplateSpec, market_data: Dict = None) -> float:
        """가격 최적화 자율 결정"""
        import random
        
        tier_ranges = {
            PricingTier.LOW: (8, 19),
            PricingTier.MID: (40, 80),
            PricingTier.HIGH: (100, 250),
            PricingTier.BUNDLE_BASIC: (49, 79),
            PricingTier.BUNDLE_PREMIUM: (99, 149),
            PricingTier.BUNDLE_ALL_ACCESS: (199, 389)
        }
        
        base_range = tier_ranges.get(spec.price_tier, (29, 79))
        base_price = random.randint(*base_range)
        
        # 시장 데이터 기반 조정
        if market_data:
            avg_price = market_data.get("average_price", base_price)
            if avg_price > base_price * 1.3:
                base_price = int(base_price * 1.1)
            elif avg_price < base_price * 0.7:
                base_price = int(base_price * 0.9)
        
        # 번들 할인 적용
        if spec.bundle_products:
            discount = random.uniform(0.30, 0.60)
            base_price = int(base_price * (1 - discount))
        
        return float(base_price)
    
    def decide_bundle_strategy(self, templates: List[TemplateSpec]) -> Dict:
        """번들 전략 자율 결정 (Thomas Frank, Easlo 벤치마킹)"""
        logger.info("Deciding bundle strategy based on successful sellers...")
        
        if len(templates) < 2:
            return {"type": "individual", "reason": "Not enough products for bundling"}
        
        prompt = f"""
Based on successful template sellers strategies:

Thomas Frank: 2-product bundles at $179 (36% discount)
Easlo: 3-10 product bundles at $199-389 (50-60% discount)
Optemization: Premium bundles with consulting add-ons

You have these templates to bundle:
{json.dumps([{"name": t.name, "features": t.features[:3]} for t in templates], indent=2)}

Decide the optimal bundle strategy:
1. Which templates to bundle together (complementary products)
2. Bundle type: basic/premium/all-access
3. Optimal price point
4. Expected conversion rate improvement

Return JSON:
- bundle_type: individual/basic/premium/all-access
- included_products: list of template IDs
- discount_rate: 0.0-1.0
- final_price: calculated price
- expected_conversion_lift: percentage improvement
- rationale: why this bundle will succeed
"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Error in bundle strategy: {e}")
            return {"type": "individual", "reason": "AI decision failed, defaulting to individual"}
    
    def _calculate_optimal_price(self, analysis: TrendAnalysis) -> float:
        import random
        price_range = analysis.recommended_price_range
        return float(random.randint(int(price_range[0]), int(price_range[1])))
    
    def _generate_bundle_decision(self, analysis: TrendAnalysis) -> List[str]:
        if analysis.trend_score > 0.8 and analysis.competition_level != "high":
            return ["bundle_candidate"]
        return []
    
    def _categorize_niche(self, niche: str) -> TemplateCategory:
        niche_lower = niche.lower()
        
        if any(w in niche_lower for w in ["budget", "finance", "money", "investment"]):
            return TemplateCategory.FINANCE
        elif any(w in niche_lower for w in ["plan", "schedule", "calendar", "organize"]):
            return TemplateCategory.PLANNING
        elif any(w in niche_lower for w in ["marketing", "content", "social", "business"]):
            return TemplateCategory.MARKETING
        elif any(w in niche_lower for w in ["educate", "course", "learn", "student"]):
            return TemplateCategory.EDUCATION
        elif any(w in niche_lower for w in ["creative", "design", "art", "creative"]):
            return TemplateCategory.CREATIVE
        elif any(w in niche_lower for w in ["business", "project", "management"]):
            return TemplateCategory.BUSINESS
        else:
            return TemplateCategory.PRODUCTIVITY
    
    def _fallback_trend_analysis(self) -> TrendAnalysis:
        return TrendAnalysis(
            niche="Productivity System",
            trend_score=0.75,
            competition_level="medium",
            growth_rate=0.12,
            recommended_price_range=(29, 79),
            top_performers=[{"name": "Ultimate Brain", "price": 129}],
            market_gap=["Beginner-friendly", "Industry-specific", "Integration-ready"],
            recommendations=["Focus on clarity", "Include video tutorials", "Add templates"],
            template_type=TemplateType.NOTION,
            bundle_opportunities=["Productivity + Finance Bundle"]
        )
    
    def _fallback_template_spec(self, analysis: TrendAnalysis) -> TemplateSpec:
        return TemplateSpec(
            name=f"{analysis.niche} Ultimate Template",
            type=analysis.template_type,
            category=self._categorize_niche(analysis.niche),
            description=f"Complete {analysis.niche} solution for professionals",
            features=["Easy setup", "Comprehensive features", "Regular updates", "Premium support"],
            target_audience="Busy Professionals",
            price_tier=PricingTier.MID,
            estimated_price=49.0,
            metadata={"fallback": True}
        )
    
    def _fallback_content(self, spec: TemplateSpec) -> Dict:
        return {
            "full_description": spec.description,
            "template_structure": ["Introduction", "Main Content", "Conclusion"],
            "page_contents": {"Introduction": "Welcome to the template"},
            "usage_guide": "1. Open template 2. Fill in your content 3. Export",
            "marketing_copy": f"Transform your {spec.category.value} with {spec.name}",
            "seo_keywords": [spec.category.value, spec.type.value, "template"]
        }
    
    def _fallback_design_prompt(self, spec: TemplateSpec) -> str:
            return f"""
Professional {spec.type.value} template design for {spec.category.value}.
Clean, modern aesthetic with clear sections for {', '.join(spec.features[:3])}.
Target: {spec.target_audience}
"""

# ✅ 지연 초기화 (주석 처리 - main.py에서 생성)
# template_ai = TemplateAIGenerator()
