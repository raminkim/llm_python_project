import asyncio
from api import naver_search_api, openAI_api, kakaomap_transfrom_address, kakaomap_rest_api
from crawlers.get_review_content import async_request_review_graphql, async_parse_review_content, async_request_place_id_graphql
from processing.review_to_json import async_review_to_json
from embeddings_db.initialize_vector_db import initialize_vector_db

from config.config import OPENAI_API_KEY

from openai import OpenAI

import re
import time


async def process_category(category: str, x: float, y: float):
    """
    특정 카테고리에 대한 리뷰를 분석하고, 결과를 반환하는 함수이다.
    """

    # OpenAI client 정의
    client = OpenAI(api_key = OPENAI_API_KEY)

    # 현재 처리중인 장소의 이름
    place_name = None

    # search_result = search_by_category(127.743288, 37.872316, "FD6", 15)
    # search_result = kakaomap_rest_api.search_by_category(127.948911, 37.350087, "FD6", 15)

    search_result = kakaomap_rest_api.search_by_category(x, y, category, 15)
    print("카카오맵 주변 카테고리 불러왔음.")

    if search_result:
        print("춘천 주변 카페 검색 결과:")

        async def process_place(place):
            try:
                place_x = place.get('x')
                place_y = place.get('y')
                road_address_name = place.get('road_address_name')
                place_name = place.get('place_name')


                documents = kakaomap_transfrom_address.transform_coordinates(place_x, place_y)['documents'][0]

                # 카카오 REST API를 이용해 좌표의 '시'를 받아오기. ex) 춘천시
                region_2depth_name = documents['region_2depth_name']

                # 카카오 REST API를 이용해 좌표의 '동'를 받아오기. ex) 명동
                region_3depth_name = documents['region_3depth_name']

                # 카카오 REST API를 이용해 받아온 json을 기반해 X, Y 좌표를 바꾸기.
                place_x, place_y = documents['x'], documents['y']

                # 네이버 지역 검색 API 기준의 place name 받아오기
                items = naver_search_api.naver_search_api(f'{region_2depth_name} {region_3depth_name} {place_name}')['items']

                # items가 비어있다면, 검색 결과가 없는 것이므로 None을 반환.
                if not items:
                    print("naver 검색 api의 검색 결과가 없습니다.")
                    return None

                # <b></b> 등 html 태그 제거
                place_name = re.sub(r"<[^>]+>", "", items[0]['title'])
                print(place_name)

                place_id = await async_request_place_id_graphql(place_name, place_x, place_y)

                if place_id:
                    print(place_id)
                    request_result = await async_request_review_graphql(place_id)
                    reviews = await async_parse_review_content(request_result)

                    review_list = []

                    # reviews 문제 X
                    for review in reviews:
                        # 리뷰 내용이 3글자 이하라면 리뷰에 포함하지 않는다.
                        if (len(review) > 3):
                            review_list.append(review)

                    print(f"review_list: {review_list}")

                    # 리뷰 데이터값 -> JSON으로 바꿔 리스트화 시키기
                    review_jsons = await async_review_to_json(review_list, client)

                    return {"place_name": place_name, "reviews": review_jsons}

            
            except Exception as e:
                print(f"process_place 오류 발생: {e}")
                return None
        
        
        tasks = [process_place(place) for place in search_result.get('documents', [])]
        results = await asyncio.gather(*tasks)

        # 전체 장소별 리뷰 데이터를 저장할 리스트
        all_places_reviews = [result for result in results if result is not None]
        # 벡터 저장소 초기화
        initialize_vector_db(all_places_reviews)

        # 사용자 쿼리 처리
        user_query = "긍정/부정을 %로 알려줘."

        # # 각 장소별로 개별 분석 수행
        # print("\n===== 각 음식점 분석 결과 =====")

        # 클라이언트에게 반환할 음식점 결과 json list
        results_json_list = []

        # 각 장소별 답변 생성
        generate_answer_tasks = [
            asyncio.to_thread(openAI_api.generate_answer, client, f"{place_data['place_name']}의 {user_query}", place_data)
            for place_data in all_places_reviews
        ]
        answers = await asyncio.gather(*generate_answer_tasks)

        # 각 답변에 대한 긍정/부정률 추출
        async def process_answer(place_data, answer):
            try:
                # 긍정률 추출 후, int casting
                match_positive = re.search(r"긍정:\s*(\d+)%", answer)
                positive_rate = int(match_positive.group(1)) if match_positive else None

                # 부정률 추출 후, int casting
                match_negative = re.search(r"부정:\s*(\d+)%", answer)
                negative_rate = int(match_negative.group(1)) if match_negative else None

                return {
                    "store_name": place_data["place_name"],
                    "positive_rate": positive_rate,
                    "negative_rate": negative_rate
                }

            except Exception as e:
                print(f"process_answer 오류 발생: {e}")
                return None
        
        # process_answer 코루틴을 직접 실행하고 await
        process_tasks = [
            process_answer(place_data, answer)
            for place_data, answer in zip(all_places_reviews, answers)
        ]
        results = await asyncio.gather(*process_tasks)

        # 결과 중 None이 아닌 것만 필터링
        results_json_list = [result for result in results if result is not None]


        return results_json_list
    else:
        print("카카오맵 API 검색 실패.")


if __name__ == "__main__":
    import time
    start_time = time.time()
    
    # FastAPI 서버가 아닌, 직접 실행 시의 동작 (예: 테스트, 백그라운드 작업)
    async def main_script():
        try:
            result = await process_category("FD6", 127.743288, 37.872316)
            print("직접 실행 결과:", result)
        except Exception as e:
            print(f"실행 중 오류 발생: {e}")

    asyncio.run(main_script())
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n총 실행 시간: {execution_time:.2f}초")