# Dockerfile

# 1. 베이스 이미지: 파이썬 3.10 슬림 버전
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 설치: requirements.txt를 먼저 복사하여 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사: app 폴더의 모든 코드를 이미지 안으로 복사
COPY ./app /app

# 5. 서버 실행: app/fastapi_cicd/flutter_fast_api.py 파일의 app 객체를 실행
CMD ["uvicorn", "app.fastapi_cicd.flutter_fast_api:app", "--host", "0.0.0.0", "--port", "8080"]