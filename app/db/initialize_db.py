import csv
import sys
import os
import MySQLdb

from openai import OpenAI

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from crawlers.get_review_content import parse_review_content, request_place_id_graphql, request_review_graphql
from processing import clean_text

import config.config

# OpenAI client 정의
client = OpenAI(api_key = config.config.OPENAI_API_KEY)

# CSV 파일의 실제 헤더 이름
HEADER_NAME_FOR_PLACE = '상호명'
HEADER_NAME_FOR_CATEGORY = '상권업종중분류코드'
HEADER_NAME_FOR_REGION = '시군구명'
HEADER_NAME_FOR_X = '경도'
HEADER_NAME_FOR_Y = '위도'

# MySQL 데이터베이스 설정
MYSQL_PASSWORD = config.config.MYSQL_PASSWORD
REVIEW_DATABASE_NAME = config.config.REVIEW_DATABASE_NAME

# 데이터베이스 설정
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': MYSQL_PASSWORD,
    'database': REVIEW_DATABASE_NAME
}

def initialize_db():
    db_connection = None
    cursor = None

    # .env 파일 로드 확인
    if not all(DB_CONFIG.values()):
        print("Error: 데이터베이스 설정이 .env 파일에 올바르게 지정되지 않았습니다.")
        return
    
    try:
        # 전체 장소별 리뷰 데이터를 저장할 리스트
        all_places_reviews = []
        processed_count = 0

        with open('소상공인시장진흥공단_상가(상권)정보_강원_202503.csv', 'r', encoding='UTF-8') as file:
            reader = csv.DictReader(file)

            for row_dict in reader:
                if processed_count >= 100: # 처음 50개 데이터 행만 처리
                    break

                place_name = row_dict[HEADER_NAME_FOR_PLACE] # 상호명
                category = row_dict[HEADER_NAME_FOR_CATEGORY] # 카테고리
                region = row_dict[HEADER_NAME_FOR_REGION] # 시군구명
                place_x = float(row_dict[HEADER_NAME_FOR_X]) # x 좌표
                place_y = float(row_dict[HEADER_NAME_FOR_Y]) # y 좌표

                print(f"{place_name}, {category}, {region}, {place_x}, {place_y}")


                place_id = request_place_id_graphql(place_name, place_x, place_y)

                print(f"{place_name}의 id: {place_id}")
                request_result = request_review_graphql(place_id)
                reviews = parse_review_content(request_result)

                review_list = []

                for review in reviews:
                    # 리뷰 내용이 3글자 이하라면 리뷰에 포함하지 않는다.
                    if (len(review) > 3):
                        review_list.append(clean_text.clean_text(review))

                print(f"리뷰 데이터: {review_list}")

                # db 장소 리스트에 추가


                processed_count+=1
            
    except Exception as e:
        print(f"예기치 않은 오류 ('{place_name}' 처리 중): {e}")
    finally:
        if cursor:
            cursor.close()
        if db_connection and db_connection.is_connected():
            db_connection.close()
            print("MySQL 연결이 종료되었습니다!")

if __name__ == "__main__":
    initialize_db()