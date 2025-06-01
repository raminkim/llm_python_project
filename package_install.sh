#!/usr/bin/env bash
set -e  # 에러 발생 시 즉시 종료

# (선택) 가상환경을 이미 만들어두셨다면, 활성화하기 위해서 아래 라인의 주석을 해제하세요.
# source .venv/bin/activate

# pip 최신화 (에러가 나도 무시하고 진행)
pip install --upgrade pip || true

# 필요 패키지 설치
pip install \
  fastapi \
  uvicorn \
  openai \
  requests \
  python-dotenv \
  lark \
  langchain-community \
  langchain-openai \
  langchain-chroma \
  pymysql \
  haversine

echo "✅ 패키지 설치 완료!"