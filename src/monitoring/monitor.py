"""Monitoring Module - System Health and Performance Tracking"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import requests

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """시스템 메트릭"""
    timestamp: datetime
    templates_published_today: int
    total_templates: int
    daily_revenue: float
    weekly_revenue: float
    platform_health: Dict[str, str]
    active_errors: List[str]
    queue_size: int
    processing_rate: float


class MonitoringSystem:
    """모니터링 시스템"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            "sales_drop": 0.50,
            "error_rate": 5,
            "queue_size": 100,
            "processing_rate_min": 0.5
        }
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    
    def collect_metrics(self, platform_stats: Dict) -> SystemMetrics:
        """메트릭 수집"""
        return SystemMetrics(
            timestamp=datetime.now(),
            templates_published_today=platform_stats.get("published_today", 0),
            total_templates=platform_stats.get("total_templates", 0),
            daily_revenue=platform_stats.get("daily_revenue", 0),
            weekly_revenue=platform_stats.get("weekly_revenue", 0),
            platform_health=platform_stats.get("platforms", {}),
            active_errors=self._get_active_errors(),
            queue_size=self._get_queue_size(),
            processing_rate=self._calculate_processing_rate()
        )
    
    def _get_active_errors(self) -> List[str]:
        """활성 에러 조회"""
        # 실제로는 로그 모니터링 시스템에서 가져옴
        return []
    
    def _get_queue_size(self) -> int:
        """대기열 크기 조회"""
        return 0
    
    def _calculate_processing_rate(self) -> float:
        """처리율 계산"""
        return 1.0  # 100%
    
    def check_alerts(self, metrics: SystemMetrics) -> List[Dict]:
        """알림 체크"""
        alerts = []
        
        # 판매량 하락 알림
        if metrics.daily_revenue > 0:
            # 실제 구현에서는 전주同期比 계산
            pass
        
        # 에러 알림
        if len(metrics.active_errors) > self.alert_thresholds["error_rate"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "message": f"High error count: {len(metrics.active_errors)}",
                "metric": "error_count",
                "value": len(metrics.active_errors)
            })
        
        # 큐 크기 알림
        if metrics.queue_size > self.alert_thresholds["queue_size"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "message": f"Queue backup: {metrics.queue_size} items",
                "metric": "queue_size",
                "value": metrics.queue_size
            })
        
        return alerts
    
    def send_alert(self, alert: Dict):
        """알림 전송"""
        message = f"[{alert['level'].upper()}] {alert['message']}"
        
        # Discord 알림
        if self.discord_webhook:
            try:
                requests.post(self.discord_webhook, json={
                    "content": message,
                    "embeds": [{
                        "title": "Template Automation Alert",
                        "description": alert["message"],
                        "color": self._get_color_for_level(alert["level"]),
                        "fields": [
                            {"name": "Metric", "value": alert.get("metric", "N/A")},
                            {"name": "Value", "value": str(alert.get("value", "N/A"))}
                        ]
                    }]
                })
            except Exception as e:
                logger.error(f"Failed to send Discord alert: {e}")
        
        # Slack 알림
        if self.slack_webhook:
            try:
                requests.post(self.slack_webhook, json={
                    "text": message,
                    "attachments": [{
                        "color": self._get_color_for_level(alert["level"]),
                        "fields": [
                            {"title": "Alert", "value": alert["message"]},
                            {"title": "Metric", "value": alert.get("metric", "N/A")},
                            {"title": "Value", "value": str(alert.get("value", "N/A"))}
                        ]
                    }]
                })
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
    
    def _get_color_for_level(self, level: AlertLevel) -> int:
        """레벨별 색상 코드"""
        colors = {
            AlertLevel.INFO: 0x00FF00,
            AlertLevel.WARNING: 0xFFFF00,
            AlertLevel.ERROR: 0xFF6600,
            AlertLevel.CRITICAL: 0xFF0000
        }
        return colors.get(level, 0x808080)
    
    def generate_daily_report(self, metrics: SystemMetrics) -> str:
        """일간 리포트 생성"""
        report = f"""
=== 📊 Template Automation Daily Report ===
Generated: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

📈 Publishing Stats:
- Templates Published Today: {metrics.templates_published_today}
- Total Templates: {metrics.total_templates}

💰 Revenue:
- Daily Revenue: ${metrics.daily_revenue:.2f}
- Weekly Revenue: ${metrics.weekly_revenue:.2f}

🔧 System Health:
"""
        
        for platform, health in metrics.platform_health.items():
            status_emoji = "✅" if health == "healthy" else "⚠️" if health == "warning" else "❌"
            report += f"- {status_emoji} {platform}: {health}\n"
        
        if metrics.active_errors:
            report += f"\n⚠️ Active Errors ({len(metrics.active_errors)}):\n"
            for error in metrics.active_errors[:5]:  # 최대 5개만
                report += f"- {error}\n"
        else:
            report += "\n✅ No active errors\n"
        
        report += f"\n📊 Processing Rate: {metrics.processing_rate:.1%}\n"
        report += f"📋 Queue Size: {metrics.queue_size}\n"
        
        return report
    
    def generate_weekly_report(self, metrics_history: List[SystemMetrics]) -> str:
        """주간 리포트 생성"""
        if not metrics_history:
            return "No data available for weekly report"
        
        total_published = sum(m.templates_published_today for m in metrics_history)
        avg_revenue = sum(m.daily_revenue for m in metrics_history) / len(metrics_history)
        total_errors = sum(len(m.active_errors) for m in metrics_history)
        
        report = f"""
=== 📊 Template Automation Weekly Report ===
Period: Last 7 days
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Publishing Summary:
- Total Templates Published: {total_published}
- Average Daily Publications: {total_published / 7:.1f}

💰 Revenue Summary:
- Total Weekly Revenue: ${sum(m.weekly_revenue for m in metrics_history):.2f}
- Average Daily Revenue: ${avg_revenue:.2f}

🔧 System Performance:
- Average Processing Rate: {sum(m.processing_rate for m in metrics_history) / len(metrics_history):.1%}
- Total Errors: {total_errors}
- Uptime: {len([m for m in metrics_history if m.processing_rate > 0.9]) / len(metrics_history):.1%}

📋 Platform Breakdown:
"""
        
        # 플랫폼별 통계
        platform_stats = {}
        for m in metrics_history:
            for platform, health in m.platform_health.items():
                if platform not in platform_stats:
                    platform_stats[platform] = {"healthy": 0, "warning": 0, "error": 0}
                platform_stats[platform][health] += 1
        
        for platform, stats in platform_stats.items():
            total_days = sum(stats.values())
            health_ratio = stats["healthy"] / total_days
            status = "✅" if health_ratio > 0.9 else "⚠️" if health_ratio > 0.7 else "❌"
            report += f"- {status} {platform}: {stats['healthy']}/{total_days} days healthy\n"
        
        return report


class PerformanceOptimizer:
    """성능 최적화 시스템"""
    
    def __init__(self):
        self.optimization_history = []
    
    def analyze_performance(self, metrics: SystemMetrics) -> Dict:
        """성능 분석"""
        recommendations = []
        
        # 처리율 분석
        if metrics.processing_rate < self.alert_thresholds["processing_rate_min"]:
            recommendations.append({
                "area": "processing",
                "suggestion": "Consider scaling up workers or reducing batch size",
                "priority": "high"
            })
        
        # 플랫폼 건강도 분석
        warning_platforms = [
            p for p, h in metrics.platform_health.items() 
            if h in ["warning", "error"]
        ]
        if warning_platforms:
            recommendations.append({
                "area": "platforms",
                "suggestion": f"Investigate platform issues: {', '.join(warning_platforms)}",
                "priority": "high"
            })
        
        # 큐 분석
        if metrics.queue_size > self.alert_thresholds["queue_size"] * 0.7:
            recommendations.append({
                "area": "queue",
                "suggestion": "Queue is building up. Consider increasing processing capacity.",
                "priority": "medium"
            })
        
        return {
            "recommendations": recommendations,
            "overall_health": self._calculate_health_score(metrics),
            "optimizations_applied": len(self.optimization_history)
        }
    
    def _calculate_health_score(self, metrics: SystemMetrics) -> float:
        """건강도 점수 계산"""
        score = 1.0
        
        # 처리율 가중치 (40%)
        score *= metrics.processing_rate * 0.4
        
        # 플랫폼 건강도 가중치 (40%)
        platform_health = [
            1.0 if h == "healthy" else 0.5 if h == "warning" else 0.0
            for h in metrics.platform_health.values()
        ]
        if platform_health:
            score *= (sum(platform_health) / len(platform_health)) * 0.4
        else:
            score *= 0.4  # 기본 점수
        
        # 에러 가중치 (20%)
        error_penalty = min(0.2, len(metrics.active_errors) * 0.02)
        score *= (1.0 - error_penalty)
        
        return max(0.0, min(1.0, score))


# Export
monitoring_system = MonitoringSystem()
performance_optimizer = PerformanceOptimizer()
