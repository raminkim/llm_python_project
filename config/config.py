from dotenv import load_dotenv
import os

# env 파일 로드
load_dotenv()

# openai api, kakao rest api, naver api 키 로드
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
KAKAO_REST_API_KEY = os.getenv('KAKAO_RESTAPI_KEY')
NAVER_API_CLIENT_ID = os.getenv('NAVER_API_CLIENT_ID')
NAVER_API_CLIENT_SECRET = os.getenv('NAVER_API_CLIENT_SECRET')
DB_PASSWORD = os.getenv('DB_PASSWORD')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
REVIEW_DATABASE_NAME = os.getenv('REVIEW_DATABASE_NAME')
