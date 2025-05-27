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

async def async_review_to_json(reviews, client:AsyncOpenAI, chunk_size=100, overlap=20):
    """
        리뷰 데이터를 JSON 형식으로 변환하는 함수.
        Args:
            # reviews (list): 리뷰 텍스트 리스트.
            client (OpenAI): OpenAI 객체.
            chunk_size (int): 각 청크의 최대 단어 수.
            overlap (int): 청크 간 겹치는 단어 수.

        Returns:
            list: JSON 형식의 리뷰 데이터 리스트.
    """
    async def process_single_review(review, idx):
        try:
            cleaned_text = await asyncio.to_thread(clean_text, review)
            chunks = await asyncio.to_thread(chunk_text, cleaned_text, chunk_size=chunk_size, overlap=overlap) if len(cleaned_text) > 100 else [cleaned_text]
            print(f"청크와 원래 텍스트 비교")
            print(f"청크: {chunks}")
            print(f"원래 리뷰 데이터: {review}")
            
            if not chunks:
                print(f"Warning: No chunks created for review {idx}")
                return None

            start_time = time.time()
            embeddings = await get_embedding(client, chunks)
            end_time = time.time()
            print(f"embedding 하는 데 걸린 시간: {end_time - start_time:.2f}")

            return {
                "text": cleaned_text,
                "chunks": [{"text": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]
            }
        except Exception as e:
            print(f"Error processing review {idx}: {e}")
            exc_str = traceback.format_exc()
            print(f"review_to_json Error: {exc_str}")
            return None

    tasks = [process_single_review(review, idx) for idx, review in enumerate(reviews, start=1)]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]  # None이 아닌 결과만 반환