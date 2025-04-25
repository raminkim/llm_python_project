import requests
import os
import sys


# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.config import KAKAO_REST_API_KEY

def transform_coordinates(longitude, latitude):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json'
    headers = {'Authorization': f'KakaoAK {KAKAO_REST_API_KEY}'}
    params = {'x': longitude, 'y': latitude}
    
    response = requests.get(url, headers=headers, params=params)
    
    # 데이터를 성공적으로 불러온 경우, code = 200
    if response.status_code == 200:
        return response.json()
    else:
        return None