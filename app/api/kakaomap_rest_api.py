from .. import config

import requests

def search_by_category(longitude, latitude, category_code, size=15):
    url = 'https://dapi.kakao.com/v2/local/search/category.json'
    headers = {'Authorization': f'KakaoAK {config.KAKAO_REST_API_KEY}'}
    params = {
        'category_group_code': category_code,
        'x': longitude,
        'y': latitude,
        'radius': 3000,  # 검색 반경 설정 (단위: 미터)
        'size': size,      # 한 페이지에 보여질 결과 개수 (최대 15)
        'sort': 'distance' # 결과를 distance를 기준으로 정렬
    }

    # API 요청
    response = requests.get(url, headers=headers, params=params)

    # 응답 처리
    if response.status_code == 200:
        return response.json()  # 성공적으로 데이터를 반환
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None  # 실패 시 None 반환



if __name__ == "__main__":
    search_result = search_by_category(127.743288, 37.872316, "FD6")

    if search_result:
        print("춘천 주변 카페 검색 결과 (일부):")
        for place in search_result.get('documents', [])[:3]:
            print(f"- {place.get('place_name')} ({place.get('road_address_name')})")
    else:
        print("카카오맵 API 검색 실패.")