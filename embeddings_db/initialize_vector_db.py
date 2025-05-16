import numpy as np

def initialize_vector_db(all_places_reviews):
    """
    메타데이터 리스트와 임베딩 벡터 리스트를 반환합니다.
    각 메타데이터 항목에는 해당 청크가 속한 장소의 이름, 청크 텍스트,
    그리고 장소 전체의 방문자 평점과 리뷰 수가 포함됩니다.

    Args:
        all_places_reviews (list): 각 요소가 장소 데이터를 담고 있는 딕셔너리 리스트.
            각 장소 딕셔너리는 'place_name', 'reviews', 'visitor_review_score', 
            'visitor_review_count' 등의 키를 가질 것으로 예상됩니다.
            'reviews'는 각 리뷰 객체의 리스트이며, 각 리뷰 객체는 'chunks' 리스트를 가집니다.
            각 'chunk'는 'text'와 'embedding'을 가집니다.

    Returns:
        tuple: (metadata_store, embedding_list)
               metadata_store: 각 청크에 대한 메타데이터 딕셔너리의 리스트.
               embedding_list: 각 청크에 대한 임베딩 벡터의 리스트.
    """
    
    metadata_store = []
    embedding_list = []
    
    for place_data in all_places_reviews:
        place_name = place_data.get("place_name")
        reviews = place_data.get("reviews")
        visitorReviewScore = place_data.get("visitorReviewScore")
        visitorReviewCount = place_data.get("visitorReviewCount")
        
        for review in reviews:
            for chunk_data in review["chunks"]:
                original_embedding_vector = chunk_data.get("embedding")

                if isinstance(original_embedding_vector, np.ndarray):
                    # NumPy 배열인 경우, Python 리스트로 변환하여 저장 (Langchain 호환성)
                    embedding_list.append(original_embedding_vector)
                else:
                    embedding_list.append(original_embedding_vector)
                
                metadata_store.append({
                    "place_name": place_name,
                    "text": chunk_data.get("text")
                })
    
    print(f"벡터 DB에 총 {len(metadata_store)}개의 청크 저장 완료")

    # 메타데이터 리스트, 그리고 임베딩 벡터 리스트를 반환
    return metadata_store, embedding_list