import requests
import os
import sys

from urllib.parse import quote

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.config import NAVER_API_CLIENT_ID
from config.config import NAVER_API_CLIENT_SECRET

def naver_search_api(keyword):
    enc_query = quote(keyword)  # 검색어를 URL 인코딩합니다.
    url = f'https://openapi.naver.com/v1/search/local.json?query={enc_query}&display=5'
    headers = {
         "X-Naver-Client-Id": NAVER_API_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_API_CLIENT_SECRET
    }

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 에러: {e}")
        return None