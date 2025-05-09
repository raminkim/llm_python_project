import time
import json
import re
import requests


from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def request_review_graphql(place_id):
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
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("요청 성공!")
        print("상태 코드:", response.status_code)
        try:
            print("응답 내용 (JSON):")
            json_data = response.json()  # 응답 JSON을 파싱하여 json_data 변수에 할당
            return response.json()  # JSON 데이터를 Python 딕셔너리로 반환
        except json.JSONDecodeError:
            print("응답 내용 (Text):")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {e}")
        if e.response is not None:
            print(f"에러 상태 코드: {e.response.status_code}")
            print(f"에러 응답 내용: {e.response.text}")
        return None
    
def request_place_id_graphql(keyword: str, x, y):
    url = 'https://map.naver.com/p/api/search/instant-search'
    params = {
    'query': keyword,
    'coords': f'{y},{x}'
    # 'coords': f'37.87336559999969,127.74447840000278'
    }
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ko-KR,ko',
    'referer': 'https://map.naver.com/p/search/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Whale/4.31.304.16 Safari/537.36'
    }

    response = requests.get(url, params=params, headers=headers)
    print("상태 코드:", response.status_code)
    if response.status_code == 200:
        for place in response.json()["place"]:
            return place["id"]
    
def parse_review_content(json_data):
    """JSON 데이터에서 리뷰 내용을 추출하는 함수."""
    try:
        # json_data가 이미 파이썬 객체인지 확인하고,
        # 문자열이 아니라면 그대로 사용
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
        
        # print("parse_review_content : ", reviews)
        return reviews
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        print(f"JSON 파싱 오류: {e}")
        return []

def get_review_content(keyword: str, driver) -> list:
    driver.get(f"https://map.naver.com/v5/search/{keyword}")
    
    result_status = search_iframe(driver)

    if result_status == "single":
        print("단일 검색 결과입니다.")
    elif result_status == "multi":
        print("다중 검색 결과입니다.")
        
        try:
            # searchIframe으로 전환
            if not switch_to_iframe(driver, 'search'):
                return []
            
            first_result = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div#_pcmap_list_scroll_container > ul > li:first-child a.ApCpt.k4f_J"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView(true);", first_result)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(first_result))
            
            driver.execute_script("arguments[0].click();", first_result)
            print("첫 번째 검색 결과를 클릭했습니다.")
            
            driver.switch_to.default_content()
            
            # entryIframe으로 전환
            if not switch_to_iframe(driver, 'entry'):
                return []
        
        except TimeoutException:
            print("검색 결과를 찾을 수 없습니다.")
        except Exception as e:
            print(f"오류 발생: {e}")
            driver.switch_to.default_content()
    


if __name__ == '__main__':
    place_id = "37127882"

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

    response = requests.post(url, headers=headers, json=payload)
    print(response.json)