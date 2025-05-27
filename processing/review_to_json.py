import asyncio
import os
import sys
import traceback
import time
from openai import AsyncOpenAI, OpenAI

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
    
from processing.clean_text import clean_text
from processing.chunk_text import chunk_text
from processing.get_embedding import get_embedding

async def async_review_to_json(review_list, client:AsyncOpenAI, chunk_size=100, overlap=20):
    """
        리뷰 데이터를 JSON 형식으로 변환하는 함수.
        Args:
            # review_list (list): 리뷰 텍스트 리스트.
            client (AsyncOpenAI): AsyncOpenAI 객체.
            chunk_size (int): 각 청크의 최대 단어 수.
            overlap (int): 청크 간 겹치는 단어 수.

        Returns:
            list: JSON 형식의 리뷰 데이터 리스트.
    """

    # 리뷰 텍스트에서 특수문자 및 이모지를 제거하고, 공백을 제거합니다.
    review_list = [clean_text(review) for review in review_list]

    # 리뷰 텍스트 길이가 100을 초과할 경우에만 청크화를 진행하고, 아니라면 리뷰 텍스트를 그대로 사용합니다.
    review_list = [
        chunk
        for review in review_list
        for chunk in (chunk_text(review) if len(review) > 100 else [review])
    ]

    embeddings = await get_embedding(client, review_list) if review_list else None

    results = [{
        "text": review,
        "chunks": [{"text": review, "embedding": embedding}]
    } for review, embedding in zip(review_list, embeddings) ]

    return [result for result in results if result is not None]  # None이 아닌 결과만 반환