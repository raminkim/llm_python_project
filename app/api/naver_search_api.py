from .. import config

import requests
import os

from urllib.parse import quote

def naver_search_api(keyword):
    print(f"naver search keyword: {keyword}")
    enc_query = quote(keyword)  # 검색어를 URL 인코딩합니다.
    url = f'https://openapi.naver.com/v1/search/local.json?query={enc_query}&display=5'
    headers = {
        "X-Naver-Client-Id": config.NAVER_API_CLIENT_ID,
        "X-Naver-Client-Secret": config.NAVER_API_CLIENT_SECRET
    }

    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"NAVER SEARCH API 요청 에러: {e}")
        return None
    

if __name__ == '__main__':
    # 기존 단일 검색 테스트
    result1 = naver_search_api("맘스터치 강원대점")
    print("단일 검색 결과:", result1)