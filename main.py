from api import naver_search_api,openAI_api, kakaomap_transfrom_address, kakaomap_rest_api

from crawlers.get_review_content import parse_review_content, request_review_graphql
from crawlers.get_review_content import request_place_id_graphql
from embeddings_db.initialize_vector_db import initialize_vector_db
from processing import analyze_sentiment, chunk_text, classify_length, clean_text, extract_keywords, get_embedding

from config.config import OPENAI_API_KEY


from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import re




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
        # sentiment = analyze_sentiment.analyze_sentiment(cleaned_text)
        keywords = extract_keywords.extract_keywords(cleaned_text)
        chunks = chunk_text.chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
        embeddings = [get_embedding.get_embedding(client, chunk) for chunk in chunks]

        review_json = {
            "index": review_index,
            "text": cleaned_text,
            "length": text_length,
            # "senitiment": sentiment,
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

    search_result = kakaomap_rest_api.search_by_category(127.948911, 37.350087, "FD6", 15)

    if search_result:
        print("춘천 주변 카페 검색 결과:")
        for place in search_result.get('documents', []):
            x = place.get('x')
            y = place.get('y')
            road_address_name = place.get('road_address_name')
            place_name = place.get('place_name')

            print(f'{road_address_name} {place_name}')

            # print(kakaomap_transfrom_address.transform_coordinates(x, y)['documents'][0])
            
            # 카카오 REST API를 이용해 좌표의 '시'를 받아오기. ex) 춘천시
            region_2depth_name = kakaomap_transfrom_address.transform_coordinates(x, y)['documents'][0]['region_2depth_name']

            # 카카오 REST API를 이용해 좌표의 '동'를 받아오기. ex) 명동
            region_3depth_name = kakaomap_transfrom_address.transform_coordinates(x, y)['documents'][0]['region_3depth_name']


            # 네이버 지역 검색 API 기준의 place name 받아오기
            items = naver_search_api.naver_search_api(f'{region_2depth_name} {region_3depth_name} {place_name}')['items']

            # items가 비어있다면, 검색 결과가 없는 것이므로 continue.
            if not items:
                print("naver 검색 api의 검색 결과가 없습니다.")
                continue
            
            # <b></b> 등 html 태그 제거
            place_name = re.sub(r"<[^>]+>", "", items[0]['title'])
            print(place_name)

            place_id = request_place_id_graphql(place_name, x, y)
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
        place_response = openAI_api.generate_answer(client, place_query, place_data)
        
        print(f"\n[{place_name}]")
        print(place_response)


