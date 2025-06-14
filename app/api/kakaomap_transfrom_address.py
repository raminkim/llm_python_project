from .. import config

import requests
import os

def transform_coordinates(longitude, latitude):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2regioncode.json'
    headers = {'Authorization': f'KakaoAK {config.KAKAO_REST_API_KEY}'}
    params = {'x': longitude, 'y': latitude}
    
    response = requests.get(url, headers=headers, params=params)
    
    # 데이터를 성공적으로 불러온 경우, code = 200
    if response.status_code == 200:
        return response.json()
    else:
        return None