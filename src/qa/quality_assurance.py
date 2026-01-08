"""Quality Assurance Module - Template Validation and Risk Management"""
import os
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class QAReport:
    """품질 검증 보고서"""
    template_id: str
    passed: bool
    checks: Dict[str, Dict]
    issues_found: List[str]
    recommendations: List[str]
    created_at: datetime
    risk_score: float


class QualityAssuranceSystem:
    """품질 보장 시스템 - 모든 배포 전 필수 검증"""
    
    def __init__(self):
        self.known_hashes_db = "template_hashes.json"
        self.forbidden_keywords = self._load_forbidden_keywords()
        self.load_hash_database()
    
    def _load_forbidden_keywords(self) -> List[str]:
        """상표권 침해 키워드 로드"""
        return [
            'adobe', 'microsoft', 'google', 'apple', 'amazon',
            'etsy', 'gumroad', 'canva', 'figma', 'notion',
            'disney', 'marvel', 'harry potter', 'star wars',
            'nike', 'adidas', 'gucci', 'prada', 'cocacola',
            'facebook', 'instagram', 'twitter', 'linkedin'
        ]
    
    def load_hash_database(self):
        """해시 데이터베이스 로드"""
        if os.path.exists(self.known_hashes_db):
            try:
                with open(self.known_hashes_db, 'r') as f:
                    self.existing_hashes = json.load(f)
            except:
                self.existing_hashes = {}
        else:
            self.existing_hashes = {}
    
    def save_hash_database(self):
        """해시 데이터베이스 저장"""
        with open(self.known_hashes_db, 'w') as f:
            json.dump(self.existing_hashes, f, indent=2)
    
    def check_duplicate_similarity(self, image_path: str = None) -> Tuple[bool, float]:
        """중복/유사 이미지 검사 (phash 알고리즘)"""
        # 이미지 경로가 없거나 파일이 존재하지 않으면 검사 건너뛰기
        if not image_path or not os.path.exists(image_path):
            logger.info("No image file provided or file not found, skipping duplicate check")
            return True, 0
            
        try:
            import imagehash
            from PIL import Image
            
            # 이미지 해시 계산
            with Image.open(image_path) as img:
                phash = imagehash.phash(img)
                current_hash = str(phash)
            
            # 기존 해시와 비교
            for existing_path, existing_hash in self.existing_hashes.items():
                distance = self._hamming_distance(current_hash, existing_hash)
                
                if distance < 5:  # 유사도 임계값
                    logger.warning(f"Similar template found: {existing_path}")
                    return False, distance
            
            # 새 해시 저장
            self.existing_hashes[image_path] = current_hash
            self.save_hash_database()
            
            return True, 0
            
        except ImportError:
            logger.warning("imagehash not available, skipping duplicate check")
            return True, 0
        except Exception as e:
            logger.error(f"Error in duplicate check: {e}")
            return True, 0  # 에러 시 통과
    
    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        """해밍 거리 계산 (phash 비교)"""
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            return abs(h1 - h2)
        except:
            return 10  # 에러 시 거리가 먼 것으로 처리
    
    def check_trademark_keywords(self, text: str) -> List[str]:
        """상표권 키워드 검사"""
        text_lower = text.lower()
        issues = []
        
        for keyword in self.forbidden_keywords:
            if keyword in text_lower:
                issues.append(f"상표권 키워드 발견: {keyword}")
                logger.warning(f"Trademark keyword found: {keyword}")
        
        return issues
    
    def check_platform_policy_compliance(self, template_data: Dict, platform: str) -> Tuple[bool, List[str]]:
        """플랫폼 정책 준수 검사"""
        issues = []
        
        # Gumroad 정책
        if platform == "gumroad":
            if len(template_data.get("description", "")) < 50:
                issues.append("Gumroad: 설명이 너무 짧습니다 (최소 50자)")
            
            if template_data.get("price", 0) < 0:
                issues.append("Gumroad: 무료 제품만 지원됩니다")
            
            if template_data.get("file_size_mb", 0) > 250:
                issues.append("Gumroad: 파일 크기가 250MB를 초과합니다")
        
        # Etsy 정책
        elif platform == "etsy":
            if len(template_data.get("description", "")) < 150:
                issues.append("Etsy: 설명이 너무 짧습니다 (최소 150자)")
            
            if template_data.get("tags", []) and len(template_data["tags"]) > 13:
                issues.append("Etsy: 태그가 13개를 초과합니다")
            
            if not template_data.get("materials", []):
                issues.append("Etsy:materials 정보가 필요합니다")
        
        # Lemon Squeezy 정책
        elif platform == "lemon_squeezy":
            prohibited = ['nft', 'crypto', 'gambling', 'adult', 'weapon']
            for item in prohibited:
                if item in template_data.get("description", "").lower():
                    issues.append(f"Lemon Squeezy: 금지된 콘텐츠 ({item})")
        
        return len(issues) == 0, issues
    
    def check_ai_generated_content(self, content: str) -> Tuple[bool, float]:
        """AI 생성 콘텐츠 검사 (Copyleaks API 활용 권장)"""
        # 기본적인 키워드 기반 검사
        ai_indicators = [
            "as an ai", "i cannot", "as a language model",
            "please note that", "it is important to note"
        ]
        
        score = 0
        for indicator in ai_indicators:
            if indicator in content.lower():
                score += 0.1
        
        # 임계값 (30%)
        passed = score < 0.30
        logger.info(f"AI content score: {score:.2%}, Passed: {passed}")
        
        return passed, score
    
    def check_seo_optimization(self, template_data: Dict) -> Tuple[bool, List[str]]:
        """SEO 최적화 검사"""
        issues = []
        
        title = template_data.get("name", "")
        description = template_data.get("description", "")
        tags = template_data.get("tags", [])
        
        if len(title) < 10:
            issues.append("제목이 너무 짧습니다")
        
        if len(description) < 50:
            issues.append("설명이 너무 짧습니다")
        
        if len(tags) < 3:
            issues.append("태그가 부족합니다 (최소 3개 권장)")
        
        # 키워드 밀도
        important_words = title.lower().split()
        if important_words:
            matches = sum(1 for word in important_words if word in description.lower())
            if matches / len(important_words) < 0.3:
                issues.append("제목 키워드가 설명에 충분히 포함되지 않았습니다")
        
        return len(issues) == 0, issues
    
    def validate_template(self, template_data: Dict, image_path: str = None, platform: str = "gumroad") -> QAReport:
        """템플릿 전체 검증"""
        logger.info(f"Validating template: {template_data.get('name')}")
        
        checks = {}
        issues = []
        recommendations = []
        
        # 1. 중복 검사
        duplicate_passed = True
        similarity_score = 0
        if image_path:
            duplicate_passed, similarity_score = self.check_duplicate_similarity(image_path)
        
        checks["duplicate_check"] = {
            "passed": duplicate_passed,
            "similarity_score": similarity_score,
            "details": "중복/유사 템플릿 검사"
        }
        
        if not duplicate_passed:
            issues.append("유사한 템플릿이 이미 존재합니다")
            recommendations.append("더 차별화된 템플릿을 제작하세요")
        
        # 2. 상표권 키워드 검사
        full_text = f"{template_data.get('name', '')} {template_data.get('description', '')}"
        trademark_issues = self.check_trademark_keywords(full_text)
        
        checks["trademark_check"] = {
            "passed": len(trademark_issues) == 0,
            "issues": trademark_issues,
            "details": "상표권 키워드 검사"
        }
        
        issues.extend(trademark_issues)
        
        # 3. 플랫폼 정책 준수
        policy_passed, policy_issues = self.check_platform_policy_compliance(template_data, platform)
        
        checks["policy_check"] = {
            "passed": policy_passed,
            "issues": policy_issues,
            "details": f"{platform} 정책 준수"
        }
        
        issues.extend(policy_issues)
        
        # 4. AI 콘텐츠 검사
        ai_passed, ai_score = self.check_ai_generated_content(full_text)
        
        checks["ai_content_check"] = {
            "passed": ai_passed,
            "ai_score": ai_score,
            "details": "AI 생성 콘텐츠 검사"
        }
        
        if not ai_passed:
            issues.append(f"AI 생성 콘텐츠 비율이 높습니다 ({ai_score:.1%})")
            recommendations.append("더 인간적인 언어로 재작성하세요")
        
        # 5. SEO 최적화
        seo_passed, seo_issues = self.check_seo_optimization(template_data)
        
        checks["seo_check"] = {
            "passed": seo_passed,
            "issues": seo_issues,
            "details": "SEO 최적화 검사"
        }
        
        issues.extend(seo_issues)
        
        # 종합 결과
        all_passed = all(check["passed"] for check in checks.values())
        
        # 리스크 점수 계산
        risk_score = (
            (0.3 if not duplicate_passed else 0) +
            (0.2 * len(trademark_issues) / 5) +
            (0.3 if not policy_passed else 0) +
            (0.2 if not ai_passed else 0)
        )
        
        return QAReport(
            template_id=template_data.get("template_id", str(datetime.now().timestamp())),
            passed=all_passed,
            checks=checks,
            issues_found=issues,
            recommendations=recommendations,
            created_at=datetime.now(),
            risk_score=min(1.0, risk_score)
        )
    
    def generate_qa_report_summary(self, report: QAReport) -> str:
        """QA 보고서 요약 생성"""
        summary = f"""
=== 품질 검증 보고서 ===
템플릿 ID: {report.template_id}
검증 시간: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}

통과 여부: {'✅ 통과' if report.passed else '❌ 실패'}
리스크 점수: {report.risk_score:.2%}

=== 개별 검사 결과 ===
"""
        for check_name, check_result in report.checks.items():
            status = '✅' if check_result['passed'] else '❌'
            summary += f"{status} {check_result['details']}\n"
        
        if report.issues_found:
            summary += f"\n=== 발견된 이슈 ({len(report.issues_found)}개) ===\n"
            for issue in report.issues_found:
                summary += f"• {issue}\n"
        
        if report.recommendations:
            summary += f"\n=== 권장사항 ===\n"
            for rec in report.recommendations:
                summary += f"• {rec}\n"
        
        return summary


class RiskManagementSystem:
    """리스크 관리 시스템 - 자율 대응"""
    
    def __init__(self):
        self.qa_system = QualityAssuranceSystem()
        self.error_counts = {}
        self.sales_history = []
    
    def assess_platform_risk(self, platform: str) -> float:
        """플랫폼 리스크 평가"""
        platform_risks = {
            "gumroad": 0.3,
            "etsy": 0.6,  # 더 엄격한 정책
            "lemon_squeezy": 0.25,
            "payhip": 0.3
        }
        
        base_risk = platform_risks.get(platform, 0.5)
        
        # 에러 이력 반영
        error_count = self.error_counts.get(platform, 0)
        if error_count > 3:
            base_risk += 0.2
        
        return min(1.0, base_risk)
    
    def should_adjust_strategy(self, metrics: Dict) -> Dict:
        """전략 조정 필요 여부 판단 (RiskThresholds 활용)"""
        from ..core.config import RiskThresholds
        
        adjustments = {}
        
        # AI 감지율太高
        if metrics.get("ai_detection_rate", 0) > RiskThresholds.AI_GENERATION_THRESHOLD:
            adjustments["ai_detection"] = {
                "action": "increase_human_review",
                "value": min(1.0, metrics["ai_detection_rate"] * 1.2)
            }
        
        # 판매량 하락
        if metrics.get("sales_drop_rate", 0) > RiskThresholds.SALES_DROP_THRESHOLD:
            adjustments["sales_decline"] = {
                "action": "price_reduction",
                "value": 0.15
            }
        
        # 플랫폼 에러
        if metrics.get("platform_errors", 0) > 5:
            adjustments["platform_issues"] = {
                "action": "diversify_platforms",
                "value": True
            }
        
        return adjustments
    
    def autonomous_response(self, scenario: str, context: Dict) -> Dict:
        """자율 대응 결정"""
        responses = {
            "ai_quality_degrade": {
                "action": "adjust_ai_parameters",
                "steps": ["increase_creativity_param", "add_human_review_step", "update_training_data"]
            },
            "platform_api_error": {
                "action": "retry_with_backoff",
                "steps": ["exponential_backoff", "switch_alternative_platform", "manual_alert"]
            },
            "sales_decline": {
                "action": "marketing_intervention",
                "steps": ["price_optimize", "update_descriptions", "social_media_promo"]
            },
            "copyright_claim": {
                "action": "immediate_takedown",
                "steps": ["hide_product", "alert_owner", "document_incident"]
            },
            "account_suspension_risk": {
                "action": "risk_mitigation",
                "steps": ["reduce_posting_frequency", "diversify_content", "backup_platform_focus"]
            }
        }
        
        return responses.get(scenario, {"action": "manual_review", "steps": ["alert_operator"]})


# Export
qa_system = QualityAssuranceSystem()
risk_system = RiskManagementSystem()
