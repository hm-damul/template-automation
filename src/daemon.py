"""
Template Automation System - 24/7 Production Daemon
✅ 24시간 365일 자동 운영
✅ 자가 진단 및 복구 시스템
✅ 헬스 모니터링
✅ 자동 재시작
"""
import os
import sys
import json
import time
import logging
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import requests

# 경로 설정
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "logs" / "daemon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HealthMonitor:
    """헬스 모니터링 시스템"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.cycle_count = 0
        self.error_count = 0
        self.last_success = None
        self.last_error = None
        self.system_status = "healthy"
        
        # 시스템 리소스 모니터링
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 80.0  # %
        self.disk_threshold = 90.0  # %
    
    def check_system_health(self) -> Dict:
        """시스템 건강 상태 체크"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.start_time),
            "cpu_usage": self._get_cpu_usage(),
            "memory_usage": self._get_memory_usage(),
            "disk_usage": self._get_disk_usage(),
            "network_status": self._check_network(),
            "cycle_count": self.cycle_count,
            "error_count": self.error_count,
            "status": "healthy"
        }
        
        # 임계값 체크
        if health["cpu_usage"] > self.cpu_threshold:
            health["status"] = "warning"
            logger.warning(f"High CPU usage: {health['cpu_usage']}%")
        
        if health["memory_usage"] > self.memory_threshold:
            health["status"] = "warning"
            logger.warning(f"High memory usage: {health['memory_usage']}%")
        
        if health["error_count"] > 10:
            health["status"] = "critical"
            logger.error("High error count detected!")
        
        self.system_status = health["status"]
        return health
    
    def _get_cpu_usage(self) -> float:
        """CPU 사용량 조회"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """메모리 사용량 조회"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def _get_disk_usage(self) -> float:
        """디스크 사용량 조회"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except:
            return 0.0
    
    def _check_network(self) -> bool:
        """네트워크 상태 확인"""
        try:
            response = requests.get("https://api.openai.com", timeout=5)
            return True
        except:
            return False
    
    def record_success(self):
        """성공 기록"""
        self.cycle_count += 1
        self.last_success = datetime.now()
    
    def record_error(self, error: str):
        """오류 기록"""
        self.error_count += 1
        self.last_error = error
        logger.error(f"Error recorded: {error}")


class ProductionDaemon:
    """24/7 프로덕션 데몬"""
    
    def __init__(self):
        self.health_monitor = HealthMonitor()
        self.is_running = False
        self.should_stop = False
        self.cycle_interval = 3600  # 1시간마다 실행
        self.max_retries = 3
        self.retry_delay = 300  # 5분 대기
        
        # 신호 처리
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("🔧 Production Daemon initialized")
    
    def _signal_handler(self, signum, frame):
        """시그널 처리"""
        logger.info(f"Received signal {signum}, preparing to stop...")
        self.should_stop = True
    
    def start(self):
        """데몬 시작"""
        logger.info("🚀 Starting Production Daemon - 24/7 Operation")
        self.is_running = True
        
        # 로그 디렉토리 생성
        logs_dir = PROJECT_ROOT / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        while not self.should_stop:
            try:
                logger.info("=" * 50)
                logger.info(f"🔄 Cycle #{self.health_monitor.cycle_count + 1} - {datetime.now()}")
                
                # 헬스 체크
                health = self.health_monitor.check_system_health()
                logger.info(f"📊 System Health: {health['status']}")
                
                # 자동화 사이클 실행
                success = self._run_automation_cycle()
                
                if success:
                    self.health_monitor.record_success()
                    logger.info("✅ Automation cycle completed successfully")
                else:
                    logger.warning("⚠️ Automation cycle failed, will retry if needed")
                    self.health_monitor.record_error("Cycle failed")
                
                # 시스템 상태 로깅
                self._log_system_status()
                
                # 다음 사이클까지 대기
                logger.info(f"💤 Sleeping for {self.cycle_interval} seconds...")
                time.sleep(self.cycle_interval)
                
            except Exception as e:
                logger.error(f"❌ Critical error in daemon loop: {e}")
                self.health_monitor.record_error(str(e))
                time.sleep(self.retry_delay)
        
        logger.info("🛑 Daemon stopped")
        self.is_running = False
    
    def _run_automation_cycle(self) -> bool:
        """자동화 사이클 실행 (재시도 포함)"""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"📦 Running automation cycle (attempt {attempt}/{self.max_retries})")
                
                # 메인 오케스트레이터 실행
                from main import TemplateAutomationOrchestrator
                
                orchestrator = TemplateAutomationOrchestrator()
                results = orchestrator.run_full_cycle()
                
                # 결과 확인
                if results.get("errors") and len(results["errors"]) > 3:
                    logger.warning(f"⚠️ Cycle had {len(results['errors'])} errors")
                    if attempt < self.max_retries:
                        logger.info(f"🔄 Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
                else:
                    # 성공 리포트 저장
                    self._save_cycle_report(results)
                    return True
                    
            except Exception as e:
                logger.error(f"Error in automation cycle (attempt {attempt}): {e}")
                self.health_monitor.record_error(str(e))
        
        return False
    
    def _save_cycle_report(self, results: Dict):
        """사이클 리포트 저장"""
        report_dir = PROJECT_ROOT / "reports"
        report_dir.mkdir(exist_ok=True)
        
        filename = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = report_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Cycle report saved: {filename}")
    
    def _log_system_status(self):
        """시스템 상태 로깅"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.health_monitor.start_time),
            "total_cycles": self.health_monitor.cycle_count,
            "total_errors": self.health_monitor.error_count,
            "last_success": self.health_monitor.last_success.isoformat() if self.health_monitor.last_success else None,
            "last_error": self.health_monitor.last_error,
            "current_status": self.health_monitor.system_status
        }
        
        # 상태 파일 업데이트
        status_file = PROJECT_ROOT / "system_status.json"
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"📊 System status updated: {status['current_status']}")
    
    def get_status(self) -> Dict:
        """데몬 상태 조회"""
        return {
            "is_running": self.is_running,
            "should_stop": self.should_stop,
            "health": self.health_monitor.check_system_health(),
            "configuration": {
                "cycle_interval": self.cycle_interval,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay
            }
        }


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Template Automation Production Daemon")
    parser.add_argument("--run-once", action="store_true", help="Run single cycle and exit")
    parser.add_argument("--status", action="store_true", help="Show daemon status")
    parser.add_argument("--health", action="store_true", help="Show health check")
    
    args = parser.parse_args()
    
    if args.status:
        daemon = ProductionDaemon()
        status = daemon.get_status()
        print(json.dumps(status, indent=2))
        
    elif args.health:
        monitor = HealthMonitor()
        health = monitor.check_system_health()
        print(json.dumps(health, indent=2))
        
    elif args.run_once:
        # 한 번만 실행
        from main import TemplateAutomationOrchestrator
        orchestrator = TemplateAutomationOrchestrator()
        results = orchestrator.run_full_cycle()
        print(json.dumps(results, indent=2))
        
    else:
        # 24/7 데몬 시작
        print("🚀 Starting Template Automation Production Daemon...")
        print("📋 This will run 24/7 with automatic health monitoring and self-healing")
        print("💡 Press Ctrl+C to stop")
        print()
        
        daemon = ProductionDaemon()
        daemon.start()


if __name__ == "__main__":
    main()
