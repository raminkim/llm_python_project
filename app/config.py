# from dotenv import load_dotenv
# from pathlib import Path

import os


# 로컬에서 사용한다면 load_dotenv 주석 해제 필요! (app 폴더 밖의 env를 읽고도록 설정)
# load_dotenv(Path(__file__).resolve().parent.parent / '.env')


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

# 데이터베이스 비밀번호
DB_PASSWORD = os.getenv("DB_PASSWORD")