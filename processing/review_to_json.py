import asyncio
import os
import sys
from openai import OpenAI

# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
    
from processing.clean_text import clean_text
from processing.classify_length import classify_length
from processing.chunk_text import chunk_text
from processing.get_embedding import get_embedding

async def async_review_to_json(reviews, client:OpenAI, chunk_size=100, overlap=20):
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
            cleaned_text = clean_text(review)
            chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)

            print(f"chunks: {chunks}")
            
            if not chunks:
                print(f"Warning: No chunks created for review {idx}")
                return None

            # asyncio.to_thread를 사용하여 동기 함수를 비동기적으로 실행
            embedding_tasks = [
                asyncio.to_thread(get_embedding, client, chunk)
                for chunk in chunks
            ]
            embeddings = await asyncio.gather(*embedding_tasks)

            return {
                "text": cleaned_text,
                "chunks": [{"text": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]
            }
        except Exception as e:
            print(f"Error processing review {idx}: {e}")
            return None

    tasks = [process_single_review(review, idx) for idx, review in enumerate(reviews, start=1)]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]  # None이 아닌 결과만 반환