from api import naver_search_api, openAI_api, kakaomap_transfrom_address, kakaomap_rest_api
from crawlers.get_review_content import parse_review_content, request_review_graphql
from crawlers.get_review_content import request_place_id_graphql
from embeddings_db.initialize_vector_db import initialize_vector_db
from processing import chunk_text, classify_length, clean_text, get_embedding

from config.config import OPENAI_API_KEY

from openai import OpenAI

import re

def review_to_json(reviews, client:OpenAI, chunk_size=300, overlap=50):
    """
        리뷰 데이터를 JSON 형식으로 변환하는 함수.
        Args:
            reviews (list): 리뷰 텍스트 리스트.
            client (OpenAI): OpenAI 객체.
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
        chunks = chunk_text.chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
        embeddings = [get_embedding.get_embedding(client, chunk) for chunk in chunks]

        review_json = {
            "index": review_index,
            "text": cleaned_text,
            "length": text_length,
            "chunks": [{"text": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]
        }

        review_jsons.append(review_json)

    return review_jsons


async def process_category(category: str, x: float, y: float):
    """
    특정 카테고리에 대한 리뷰를 분석하고, 결과를 반환하는 함수이다.
    """

    # OpenAI client 정의
    client = OpenAI(api_key = OPENAI_API_KEY)

    # 전체 장소별 리뷰 데이터를 저장할 리스트
    all_places_reviews = []

    # search_result = search_by_category(127.743288, 37.872316, "FD6", 15)


    # search_result = kakaomap_rest_api.search_by_category(127.948911, 37.350087, "FD6", 15)

    search_result = kakaomap_rest_api.search_by_category(x, y, category, 15)
    print("카카오맵 주변 카테고리 불러왔음.")

    if search_result:
        print("춘천 주변 카페 검색 결과:")
        for place in search_result.get('documents', []):
            place_x = place.get('x')
            place_y = place.get('y')
            road_address_name = place.get('road_address_name')
            place_name = place.get('place_name')

            try:
                documents = kakaomap_transfrom_address.transform_coordinates(place_x, place_y)['documents'][0]

                # 카카오 REST API를 이용해 좌표의 '시'를 받아오기. ex) 춘천시
                region_2depth_name = documents['region_2depth_name']

                # 카카오 REST API를 이용해 좌표의 '동'를 받아오기. ex) 명동
                region_3depth_name = documents['region_3depth_name']

                # 카카오 REST API를 이용해 받아온 json을 기반해 X, Y 좌표를 바꾸기.
                place_x, place_y = documents['x'], documents['y']


                # 네이버 지역 검색 API 기준의 place name 받아오기
                items = naver_search_api.naver_search_api(f'{region_2depth_name} {region_3depth_name} {place_name}')['items']

                # items가 비어있다면, 검색 결과가 없는 것이므로 continue.
                if not items:
                    print("naver 검색 api의 검색 결과가 없습니다.")
                    continue

                # <b></b> 등 html 태그 제거
                place_name = re.sub(r"<[^>]+>", "", items[0]['title'])
                print(place_name)

                place_id = request_place_id_graphql(place_name, place_x, place_y)
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
                    review_jsons = review_to_json(review_list, client)

                    all_places_reviews.append({"place_name": place_name, "reviews": review_jsons})
            except Exception as e:
                print(f"오류 발생: {e}")
                continue
            
        # 벡터 저장소 초기화
        initialize_vector_db(all_places_reviews)

        # 사용자 쿼리 처리
        user_query = "긍정/부정을 %로 알려줘."

        # # 각 장소별로 개별 분석 수행
        # print("\n===== 각 음식점 분석 결과 =====")

        # 클라이언트에게 반환할 음식점 결과 json list
        results_json_list = []
        
        for place_data in all_places_reviews:
            place_name = place_data["place_name"]

            # 해당 장소에 특화된 분석 수행
            place_query = f"{place_name}의 {user_query}"
            place_response = openAI_api.generate_answer(client, place_query, place_data)

            print(f"\n[{place_name}]")
            print(type(place_response))
            print(f"리뷰 결과: \n {place_response}")
            



            # 긍정률 추출 후, int casting
            match_positive = re.search(r"긍정:\s*(\d+)%", place_response)
            positive_rate = int(match_positive.group(1)) if match_positive else None

            # 부정률 추출 후, int casting
            match_negative = re.search(r"부정:\s*(\d+)%", place_response)
            negative_rate = int(match_negative.group(1)) if match_negative else None


            # 가게 이름, 긍정률, 부정률을 json화
            result_json = {
                "store_name": place_name,
                "positive_rate": positive_rate,
                "negative_rate": negative_rate
            }
            results_json_list.append(result_json)

        return results_json_list
    else:
        print("카카오맵 API 검색 실패.")


if __name__ == "__main__":
    # FastAPI 서버가 아닌, 직접 실행 시의 동작 (예: 테스트, 백그라운드 작업)
    async def main_script():
        result = await process_category("FD6")
        print("직접 실행 결과:", result)

    import asyncio
    asyncio.run(main_script())