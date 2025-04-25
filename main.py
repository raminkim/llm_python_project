from api.kakaomap_rest_api import search_by_category
from api.naver_search_api import naver_search_api
from api.openAI_api import generate_answer
from crawlers.get_review_content import parse_review_content, request_review_graphql
from crawlers.get_review_content import request_place_id_graphql
from embeddings_db.initialize_vector_db import initialize_vector_db

from config.config import OPENAI_API_KEY


from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import re

from processing import analyze_sentiment, chunk_text, classify_length, clean_text, extract_keywords, get_embedding


def review_to_json(reviews, chunk_size=300, overlap=50):
    """
        리뷰 데이터를 JSON 형식으로 변환하는 함수.
        Args:
            reviews (list): 리뷰 텍스트 리스트.
            chunk_size (int): 각 청크의 최대 단어 수.
            overlap (int): 청크 간 겹치는 단어 수.
        Returns:
            list: JSON 형식의 리뷰 데이터 리스트.
    """
    review_jsons = []

    for idx, review in enumerate(reviews, start=1):
        review_index = f"review_{idx:03}"
        cleaned_text = clean_text.clean_text(review)
        text_length = classify_length.classify_length(cleaned_text)
        sentiment = analyze_sentiment.analyze_sentiment(cleaned_text)
        keywords = extract_keywords.extract_keywords(cleaned_text)
        chunks = chunk_text.chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
        embeddings = [get_embedding.get_embedding(client, chunk) for chunk in chunks]

        review_json = {
            "index": review_index,
            "text": cleaned_text,
            "length": text_length,
            "senitiment": sentiment,
            "keywords": keywords,
            "chunks": [{"text": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]
        }
    
        review_jsons.append(review_json)

    return review_jsons


if __name__ == "__main__":

    # OpenAI client 정의
    client = OpenAI(api_key = OPENAI_API_KEY)

    # 전체 장소별 리뷰 데이터를 저장할 리스트
    all_places_reviews = []

    # search_result = search_by_category(127.743288, 37.872316, "FD6", 15)

    search_result = search_by_category(127.948911, 37.350087, "FD6", 15)

    # ChromeOptions 설정 및 WebDriver 초기화 (루프 외부에서 한 번만 수행)
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=chrome_options)

    if search_result:
        print("춘천 주변 카페 검색 결과:")
        for place in search_result.get('documents', []):
            x = place.get('x')
            y = place.get('y')
            road_address_name = place.get('road_address_name')
            place_name = place.get('place_name')

            print(road_address_name, place_name, x, y)

            # 네이버 지역 검색 API 기준의 place name
            for item in naver_search_api(place_name, x, y)['items']:
                if road_address_name in item.get('roadAddress', ''):
                    title = item['title']
                    # <b></b> 등 html 태그 제거
                    cleaned_title = re.sub(r"<[^>]+>", "", title)
                    print(cleaned_title)
                    break

            place_id = request_place_id_graphql(cleaned_title, x, y)
            if place_id:
                print(place_id)
            request_result = request_review_graphql(place_id)
            reviews = parse_review_content(request_result)
            review_list = []

            for review in reviews:
                # 리뷰 내용이 3글자 이하라면 리뷰에 포함하지 않는다.
                    if (len(review) > 3):
                        review_list.append(review)
            
           # 리뷰 데이터값 -> JSON으로 바꿔 리스트화 시키기
            review_jsons = review_to_json(review_list)

            all_places_reviews.append({"place_name": place_name, "reviews": review_jsons})
    
            # 벡터 저장소 초기화
            initialize_vector_db(all_places_reviews)
            
    else:
        print("카카오맵 API 검색 실패.")


    # 사용자 쿼리 처리
    user_query = "긍정/부정을 %로 알려줘."
        
    # 각 장소별로 개별 분석 수행
    print("\n===== 각 음식점 분석 결과 =====")
    
    for place_data in all_places_reviews:
        place_name = place_data["place_name"]
        
        # 해당 장소에 특화된 분석 수행
        place_query = f"{place_name}의 {user_query}"
        place_response = generate_answer(client, place_query, place_data)
        
        print(f"\n[{place_name}]")
        print(place_response)


