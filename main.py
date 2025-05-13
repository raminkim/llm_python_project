import asyncio
from api import naver_search_api, openAI_api, kakaomap_transfrom_address, kakaomap_rest_api
from crawlers.get_review_content import async_request_review_graphql, async_parse_review_content, async_request_place_id_graphql
from processing.review_to_json import async_review_to_json
from embeddings_db.initialize_vector_db import initialize_vector_db

from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

import re
import time
import os


async def process_category(category: str, x: float, y: float):
    """
    특정 카테고리에 대한 리뷰를 분석하고, 결과를 반환하는 함수이다.
    """

    # OpenAI client 정의
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY")) # gemini 2.0 나 2.5 flash 2.5로 변경해보기

    # 현재 처리중인 장소의 이름
    place_name = None

    # search_result = search_by_category(127.743288, 37.872316, "FD6", 15)
    # search_result = kakaomap_rest_api.search_by_category(127.948911, 37.350087, "FD6", 15)

    search_result = kakaomap_rest_api.search_by_category(x, y, category, 15)

    coordinate_dict = {}
    

    if search_result:
        print("카카오맵 주변 카테고리 불러오기 성공!")
        print("춘천 주변 카페 검색 결과:")

        async def process_place(place):
            try:
                place_x = place.get('x')
                place_y = place.get('y')
                road_address_name = place.get('road_address_name')
                place_name = place.get('place_name')

                coordinate_dict[place_name] = [place_x, place_y]


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

        # 모든 장소의 리뷰 데이터를 FAISS 벡터 DB에 저장, FAISS 인덱스, 메타데이터 리스트, 그리고 임베딩 벡터 리스트를 반환
        metadata_store, embedding_list = initialize_vector_db(all_places_reviews)


        # Langchain FAISS 벡터 저장소 생성
        if metadata_store and embedding_list:
            # Langchain을 위한 text:embedding pair를 리스트로 만들기기
            texts_list = [item["text"] for item in metadata_store]

            # 쿼리 임베딩용 모델
            query_embedding_function = OpenAIEmbeddings(
                model = "text-embedding-3-small", # get_embedding.py와 같은 임베딩 모델
                openai_api_key = os.getenv("OPENAI_API_KEY")
            )

            # generate_answer 함수에 전달할 langchain_vector_store 객체
            langchain_vector_store = Chroma(
                collection_name = "review_collection_chroma",
                embedding_function = query_embedding_function,
            )
            print("정보: 빈 Chroma 벡터 저장소 객체가 생성되었습니다.")

            langchain_vector_store.add_texts(
                texts=texts_list,
                embeddings=embedding_list,  # 미리 계산된 임베딩 벡터 리스트
                metadatas=metadata_store,
            )
        
        else:
            print("오류: Chroma 벡터 저장소를 생성하지 못하였습니다.")

        # # 각 장소별로 개별 분석 수행
        print("\n===== 각 음식점 분석 결과 =====")

        # 클라이언트에게 반환할 음식점 결과 json list
        results_json_list = []

        queries = [f"{place_data['place_name']}의 을 장소명으로 가진 리뷰에서 긍정적인 내용과 부정적인 내용을 찾아서 비율을 알려줘." for place_data in all_places_reviews]
        # 각 장소별 답변 생성
        # generate_answer_tasks = [
        #     asyncio.to_thread(
        #         openAI_api.generate_answer,
        #         f"{place_data['place_name']}의 을 장소명으로 가진 리뷰에서 긍정적인 내용과 부정적인 내용을 찾아서 비율을 알려줘.",
        #         langchain_vector_store,
        #         place_data['place_name']
        #     )s
        #     for place_data in all_places_reviews
        # ]
        # answers = await asyncio.gather(*generate_answer_tasks)

        start_time = time.time()
        answers = await openAI_api.generate_answer(queries, langchain_vector_store, place_name)
        end_time = time.time()
        print(f"답변 생성 시간: {end_time - start_time}")

        # 각 답변에 대한 긍정/부정률 추출
        async def process_answer(place_data, answer):
            try:
                # 긍정률 추출 후, int casting
                match_positive = re.search(r"긍정:\s*(\d+)%", answer)
                positive_rate = int(match_positive.group(1)) if match_positive else None

                # 부정률 추출 후, int casting
                match_negative = re.search(r"부정:\s*(\d+)%", answer)
                negative_rate = int(match_negative.group(1)) if match_negative else None

                coordinate_list = coordinate_dict[place_data["place_name"]]

                return {
                    "store_name": place_data["place_name"],
                    "positive_rate": positive_rate,
                    "negative_rate": negative_rate,
                    "x": coordinate_list[0],
                    "y": coordinate_list[1]
                }

            except Exception as e:
                print(f"process_answer 오류 발생: {e}")
                return None
        
        # process_answer 병렬처리
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
    
    load_dotenv()
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