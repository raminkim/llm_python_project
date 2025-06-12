# 로컬에서 사용한다면 load_dotenv 주석 해제 필요! (app 폴더 밖의 env를 읽고도록 설정)
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

import os

# 카카오맵 REST API KEY
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# OpenAI API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Google Gemini API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 네이버 검색 API 클라이언트 ID
NAVER_API_CLIENT_ID = os.getenv("NAVER_API_CLIENT_ID")

# 네이버 검색 API 클라이언트 시크릿
NAVER_API_CLIENT_SECRET = os.getenv("NAVER_API_CLIENT_SECRET")


# --- 데이터베이스 접속 정보 ---

# 데이터베이스 호스트 주소
DB_HOST = os.getenv("DB_HOST")

# 데이터베이스 포트 번호
DB_PORT = int(os.getenv("DB_PORT", 3306))

# 데이터베이스 사용자 이름
DB_USER = os.getenv("DB_USER")

# 데이터베이스 비밀번호
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 데이터베이스 이름
DB_NAME = os.getenv("DB_NAME")

# --- SQLAlchemy 데이터베이스 접속 URL ---

# 위에서 불러온 정보들을 조합하여 데이터베이스 접속 URL을 생성합니다.
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"