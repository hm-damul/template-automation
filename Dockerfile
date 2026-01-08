# Template Automation System - Production Dockerfile

# Python 3.11 slim image (작고 가벼운 프로덕션용)
FROM python:3.11-slim

# 메타데이터
LABEL maintainer="template-automation"
LABEL description="24/7 Template Automation Production System"
LABEL version="1.0.0"

# 작업 디렉토리
WORKDIR /app

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src/

# n8n 폴더 구조 생성 (대시보드용)
RUN mkdir -p /app/n8n/workflows && touch /app/n8n/workflows/placeholder.json

COPY .env.example .env

# logs 및 reports 디렉토리 생성
RUN mkdir -p /app/logs /app/reports && chmod 777 /app/logs /app/reports

# 포트 노출 (Flask API용)
EXPOSE 5000

# 헬스체크
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# 실행 명령
CMD ["python", "src/daemon.py"]
