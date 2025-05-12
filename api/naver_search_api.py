import requests
import os

from urllib.parse import quote

def naver_search_api(keyword):
    enc_query = quote(keyword)  # 검색어를 URL 인코딩합니다.
    url = f'https://openapi.naver.com/v1/search/local.json?query={enc_query}&display=5'
    headers = {
         "X-Naver-Client-Id": os.getenv("NAVER_API_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_API_CLIENT_SECRET")
    }

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 에러: {e}")
        return None