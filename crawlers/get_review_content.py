import asyncio
import time
import json
import re
import aiohttp
import requests


from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib

# 상수 정의
DEFAULT_TIMEOUT = 10
IFRAME_IDS = {
    'search': 'searchIframe',
    'entry': 'entryIframe'
}

def switch_to_iframe(driver, iframe_type, timeout=DEFAULT_TIMEOUT):
    """
    지정된 iframe으로 전환하는 유틸리티 함수
    
    Args:
        driver: WebDriver 인스턴스
        iframe_type: 'search' 또는 'entry'
        timeout: 타임아웃 시간 (초)
    
    Returns:
        bool: iframe 전환 성공 여부
    """
    try:
        iframe_id = IFRAME_IDS.get(iframe_type)
        if not iframe_id:
            raise ValueError(f"Unknown iframe type: {iframe_type}")
            
        WebDriverWait(driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, iframe_id))
        )
        print(f"{iframe_id}으로 전환 완료.")
        return True
    except TimeoutException:
        print(f"{iframe_id} 전환 실패: 타임아웃")
        return False
    except Exception as e:
        print(f"{iframe_id} 전환 중 오류 발생: {e}")
        return False

def search_iframe(driver):
    try:
        # searchIframe으로 전환
        if not switch_to_iframe(driver, 'search'):
            return "single"
            
        # 검색 결과가 하나인지 여러개인지 확인
        if driver.find_elements(By.CSS_SELECTOR, "div#_pcmap_list_scroll_container > ul > li"):
            return "multi"
        else:
            return "single"
    except Exception as e:
        print(f"iframe 검색 중 오류 발생: {e}")
        return "single"

def extract_place_id(keyword, driver):
    """
    네이버 지도에서 장소 ID를 추출하는 함수
    
    Args:
        keyword: 검색 키워드
        driver: WebDriver 인스턴스
    
    Returns:
        str or None: 추출된 장소 ID 또는 None
    """
    # 장소 ID를 추출하기 위한 URL 패턴 정의
    # 각 패턴은 네이버 지도에서 사용되는 다양한 URL 형식을 커버
    PLACE_ID_PATTERNS = {
        'marker': r'/p/api/nplace/marker/(\d+)',      # 마커 API에서 사용되는 ID 패턴
        'home': r'home\?from=map.*?&id=(\d+)',        # 홈페이지 URL에서 사용되는 ID 패턴
        'place': r'place/(\d+)',                      # 일반 장소 URL에서 사용되는 ID 패턴
        'restaurant': r'restaurant/(\d+)'             # 음식점 URL에서 사용되는 ID 패턴
    }
    
    # 로그 필터링을 위한 조건 설정
    # Network.requestWillBeSent 메시지만 필터링하여 필요한 로그만 처리
    log_filter = {
        'level': 'INFO',
        'message': {
            'method': 'Network.requestWillBeSent'
        }
    }
    
    try:
        # 1. 성능 로그 가져오기
        logs = driver.get_log('performance')
        filtered_logs = []
        
        # 2. 로그 필터링 및 파싱
        for log in logs:
            try:
                # JSON 형식의 로그 메시지 파싱
                message = json.loads(log['message'])['message']
                
                # Network.requestWillBeSent 메시지이고 URL이 있는 경우만 필터링
                if (message.get('method') == 'Network.requestWillBeSent' and 
                    'params' in message and 
                    'request' in message['params'] and 
                    'url' in message['params']['request']):
                    filtered_logs.append(message)
            except (json.JSONDecodeError, KeyError):
                # JSON 파싱 오류나 키 오류는 무시하고 다음 로그 처리
                continue
        
        # 3. 필터링된 로그에서 장소 ID 추출
        for log in filtered_logs:
            url = log['params']['request']['url']
            
            # 각 패턴에 대해 매칭 시도
            for pattern_name, pattern in PLACE_ID_PATTERNS.items():
                match = re.search(pattern, url)
                if match:
                    place_id = match.group(1)
                    print(f"장소 ID 추출 성공 (패턴: {pattern_name}): {place_id}")
                    return place_id
        
        # 4. 장소 ID를 찾지 못한 경우
        print("장소 ID를 찾을 수 없습니다.")
        print("수동으로 확인해 보세요: 개발자 도구 → Network 탭 → 'nplace' 또는 'marker' 검색")
        return None
        
    except Exception as e:
        # 5. 예상치 못한 오류 처리
        print(f"장소 ID 추출 중 오류 발생: {e}")
        return None

async def async_request_review_graphql(place_id):
    url = 'https://api.place.naver.com/graphql'
    headers = {
        'accept': '*/*',
        'accept-language': 'ko',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://pcmap.place.naver.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Whale/4.31.304.16 Safari/537.36',
    }
    payload = [{
        "operationName": "getVisitorReviews",
        "variables": {
            "input": {
                "businessId": place_id,
                "businessType": "restaurant",
                "item": "0",
                "page": 5,
                "size": 10,
                "isPhotoUsed": False,
                "sort": "recent",
                "includeContent": True,
                "getUserStats": True,
                "includeReceiptPhotos": True,
                "cidList": ["220036", "220051", "220552", "221043"],
                "getReactions": True,
                "getTrailer": True
            }
        },
        "query": "query getVisitorReviews($input: VisitorReviewsInput) {\n  visitorReviews(input: $input) {\n    items {\n      id\n      reviewId\n      rating\n      author {\n        id\n        nickname\n        from\n        imageUrl\n        borderImageUrl\n        objectId\n        url\n        review {\n          totalCount\n          imageCount\n          avgRating\n          __typename\n        }\n        theme {\n          totalCount\n          __typename\n        }\n        isFollowing\n        followerCount\n        followRequested\n        __typename\n      }\n      body\n      thumbnail\n      media {\n        type\n        thumbnail\n        thumbnailRatio\n        class\n        videoId\n        videoUrl\n        trailerUrl\n        __typename\n      }\n      tags\n      status\n      visitCount\n      viewCount\n      visited\n      created\n      reply {\n        editUrl\n        body\n        editedBy\n        created\n        date\n        replyTitle\n        isReported\n        isSuspended\n        status\n        __typename\n      }\n      originType\n      item {\n        name\n        code\n        options\n        __typename\n      }\n      language\n      highlightRanges {\n        start\n        end\n        __typename\n      }\n      apolloCacheId\n      translatedText\n      businessName\n      showBookingItemName\n      bookingItemName\n      votedKeywords {\n        code\n        iconUrl\n        iconCode\n        name\n        __typename\n      }\n      userIdno\n      loginIdno\n      receiptInfoUrl\n      reactionStat {\n        id\n        typeCount {\n          name\n          count\n          __typename\n        }\n        totalCount\n        __typename\n      }\n      hasViewerReacted {\n        id\n        reacted\n        __typename\n      }\n      nickname\n      showPaymentInfo\n      visitCategories {\n        code\n        name\n        keywords {\n          code\n          name\n          __typename\n        }\n        __typename\n      }\n      representativeVisitDateTime\n      showRepresentativeVisitDateTime\n      __typename\n    }\n    starDistribution {\n      score\n      count\n      __typename\n    }\n    hideProductSelectBox\n    total\n    showRecommendationSort\n    itemReviewStats {\n      score\n      count\n      itemId\n      starDistribution {\n        score\n        count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
    }]
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"graphql 요청 실패: {response.status}")
                return None
    
# async def async_request_place_id_graphql(keyword: str, x, y):
#     url = 'https://map.naver.com/p/api/search/instant-search'
#     params = {
#     'query': keyword,
#     'coords': f'{y},{x}'
#     # 'coords': f'37.87336559999969,127.74447840000278'
#     }
#     headers = {
#     'accept': 'application/json, text/plain, */*',
#     'accept-language': 'ko-KR,ko',
#     'referer': 'https://map.naver.com/p/search/',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Whale/4.31.304.16 Safari/537.36'
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, params=params, headers=headers) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 for place in data["place"]:
#                     print(f"place: {place}")
#                     return place["id"]
#             else:
#                 print(f"place_id 요청 실패: {response.status}")
#                 return None

async def async_request_place_id_graphql(keyword: str, x, y):
    """
    네이버 지도에서 특정 키워드로 장소를 검색하고,
    검색 결과 페이지의 HTML에서 window.__APOLLO_STATE__를 파싱하여
    첫 번째 장소의 ID, 현재 영업 상태, 상태 설명, 별점, 리뷰 개수를 반환합니다.

    Args:
        keyword (str): 검색할 장소 키워드.
        x (str or float): 검색 기준점의 clientY 좌표 (보통 경도값이나 화면 Y좌표).
        y (str or float): 검색 기준점의 clientX 좌표 (보통 위도값이나 화면 X좌표).
                           네이버 파라미터상 clientX가 y, clientY가 x로 사용됨.

    Returns:
        tuple: (place_id, status, status_description, visitorReviewScore, visitorReviewCount)
               추출 실패 시 해당 값은 None으로 반환될 수 있습니다.
               HTTP 요청 실패 시 (None, None, None, None, None) 및 오류 메시지를 출력합니다.
    """
    url = "https://pcmap.place.naver.com/place/list"

    # Referer 헤더의 URL 경로에 포함될 키워드는 URL 인코딩 (공백은 %20 등으로 처리)
    encoded_keyword_for_referer_path = urllib.parse.quote(keyword)

    # 요청 파라미터
    params = {
        'query': keyword,
        'x': '127.727872',  # 예시 좌표
        'y': '37.905947',   # 예시 좌표
        'clientX': y,
        'clientY': x,
        'display': '40',
        # mapUrl 값은 "https://map.naver.com/p/search/키워드" 형태이며,
        # requests가 이 전체 문자열을 URL 쿼리 파라미터 값으로 인코딩합니다.
        'mapUrl': f"https://map.naver.com/p/search/{keyword}",
        'svcName': 'map_pcv5',
        'searchText': keyword
    }

    # 요청 헤더
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=0, i',
        'referer': f"https://map.naver.com/p/search/{encoded_keyword_for_referer_path}",
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Whale/4.31.304.16 Safari/537.36'
    }

    # 에러 메시지
    error_message = None
    # place ID (고유)
    place_id_str = None
    # status (영업 전, 영업 중, 영업 종료)
    status = None
    # status에 대한 설명
    status_description = None
    # 장소 방문자 평점
    visitorReviewScore = None
    # 장소 방문자 리뷰 개수
    visitorReviewCount = None

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:

                # 응답 텍스트를 비동기적으로 읽어옴
                html_content = await response.text(encoding='UTF-8')
                # # 디버깅용 (html_content 출력)
                with open('html_content.txt', 'a', encoding='utf-8') as f:
                    f.write(html_content+"\n")
                    f.write("="*40+"\n")
                    

                try:
                    # 1. window.__APOLLO_STATE__ JSON 문자열 추출
                    apollo_match = re.search(r"window\.__APOLLO_STATE__\s*=\s*({.*?});", html_content, re.DOTALL)
                    
                    if not apollo_match:
                        error_message = "window.__APOLLO_STATE__를 찾을 수 없습니다."
                    else:
                        apollo_state_result = apollo_match.group(1)
                        
                        # 2. window.__APOLLO_STATE__ 찾아 JSON 파싱
                        apollo_state_json = json.loads(apollo_state_result)

                        # 3. 위 JSON에서 ROOT_QUERY 찾기
                        root_query = apollo_state_json.get("ROOT_QUERY")

                        if not root_query:
                            error_message = "ROOT_QUERY를 찾을 수 없습니다."
                        else:
                            places_result_data = None
                            for key, value in root_query.items():
                                # 4. 장소 검색 결과(PlacesResult) 찾기
                                if isinstance(value, dict) and value.get("__typename") == "PlacesResult" and "items" in value:
                                    places_result_data = value
                                    break
                            
                            if not places_result_data:
                                error_message = "장소 검색 결과(PlacesResult)를 찾을 수 없습니다."
                            else:
                                # 5. 장소 목록(items) 찾기
                                items = places_result_data.get("items")

                                if not items:
                                    error_message = "장소 목록(items)이 없습니다."
                                else:
                                    # 6. 첫 번째 장소의 place ID (= PlaceSummary 값) 가져오기
                                    first_item_reference = items[0]
                                    place_id_str = first_item_reference.get('__ref')
                                    
                                    if not place_id_str:
                                        error_message = "첫 번째 장소의 PlaceSummary 값을 찾을 수 없습니다."
                                    else:
                                        # 7. 첫 번째 장소의 place ID를 이용해 상세 정보를 가져오기
                                        place_details = apollo_state_json.get(place_id_str)

                                        if not place_details:
                                            error_message = f"'{place_id_str}'에 해당하는 장소 상세 정보를 찾을 수 없습니다."
                                        else:
                                            # 8. 장소 ID 추출
                                            place_id_str = place_details.get("id")

                                            if not place_id_str:
                                                error_message = "장소 ID를 상세 정보(place_details)에서 찾을 수 없습니다."

                                            # 8-1. 장소 방문자 평점 추출
                                            visitorReviewScore = place_details.get("visitorReviewScore")

                                            if not visitorReviewScore:
                                                error_message = "장소 방문자 평점을 상세 정보(place_details)에서 찾을 수 없습니다."

                                            # 8-2. 장소 방문자 리뷰 개수 추출
                                            visitorReviewCount = place_details.get("visitorReviewCount")

                                            if not visitorReviewScore:
                                                error_message = "장소 방문자 리뷰 개수를 상세 정보(place_details)에서 찾을 수 없습니다."
                                            
                                            # 8-3. 장소 전화번호 추출
                                            phone_number = place_details.get("phone")

                                            if not phone_number:
                                                error_message = "장소 전화번호를 상세 정보(place_details)에서 찾을 수 없습니다."

                                            # 8-4. 위도 추출
                                            latitude = place_details.get("y")
                                            if not latitude:
                                                error_message = "위도를 상세 정보(place_details)에서 찾을 수 없습니다."

                                            # 8-5. 경도 추출
                                            longitude = place_details.get("x")
                                            if not longitude:
                                                error_message = "경도를 상세 정보(place_details)에서 찾을 수 없습니다."
                                            

                                            # 9. 영업 중인지에 대한 정보를 가져오기
                                            newBusinessHours = place_details.get("newBusinessHours")
                                            
                                            # 만약 영업에 대한 정보(newBusinessHours)가 null이라면, 네이버 지도에는 해당 정보가 없는 것이다.
                                            if not newBusinessHours:
                                                error_message = "영업에 대한 정보(newBusinessHours)를 상세 정보(place_details)에서 찾을 수 없습니다."
                                            else:
                                                status = newBusinessHours["status"]
                                                status_description = newBusinessHours["description"]

                                    

                except Exception as e:
                    error_message = f"정보 추출 중 알 수 없는 오류 발생: {str(e)}"

        
                print(f"=== request_place_id_graphql 결과 ===")
                if error_message:
                    print(error_message)
                print(f"{keyword}의 id = {place_id_str}, 현재 영업 정보 = {status}, 영업 정보 description = {status_description}")
                print(f"{keyword}의 별점 = {visitorReviewScore} 점(리뷰 {visitorReviewCount}개 기반)")

                return place_id_str, status, status_description, visitorReviewScore, visitorReviewCount, phone_number, latitude, longitude
            
            else:
                # HTTP 요청 실패 (response.status_code != 200)
                print(f"API 요청 실패: HTTP 상태 코드 {response.status_code}")


async def async_parse_review_content(json_data):
    """JSON 데이터에서 리뷰 내용을 추출하는 함수."""
    try:
        if not isinstance(json_data, str):
            data = json_data
        else:
            data = json.loads(json_data)

        reviews = []
        # 최상위가 리스트이므로, 리스트의 각 요소에 접근
        for item in data:
            # 각 요소가 딕셔너리이므로 'data' 키로 접근
            visitor_reviews = item.get('data', {}).get('visitorReviews', {})
            if visitor_reviews:
                for review_item in visitor_reviews.get('items', []):
                    if 'body' in review_item:
                        reviews.append(review_item['body'])
        
        return reviews
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        print(f"JSON 파싱 오류: {e}")
        return []
    


if __name__ == '__main__':
    x = "127.727872"
    y = "37.905947"
    async_request_place_id_graphql("만석식당 강원대점", x, y)