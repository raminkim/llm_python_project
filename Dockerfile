# 1. 베이스 이미지
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사 (📌 ./app을 /app/app에 복사)
COPY ./app /app/app

# 5. PYTHONPATH를 /app/app으로 설정해줘야 import 가능
ENV PYTHONPATH=/app/app

# 6. FastAPI 서버 실행
CMD ["uvicorn", "fastapi_cicd.flutter_fast_api:app", "--host", "0.0.0.0", "--port", "8080"]