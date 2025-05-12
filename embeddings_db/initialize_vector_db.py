import numpy as np
import faiss

def initialize_vector_db(all_places_reviews):
    """
    모든 장소의 리뷰 데이터를 FAISS 벡터 DB에 저장하고,
    FAISS 인덱스, 메타데이터 리스트, 그리고 임베딩 벡터 리스트를 반환
    """    
    embedding_dim = 1536  # text-embedding-3-small 차원

    faiss_index = faiss.IndexFlatL2(embedding_dim)
    
    metadata_store = []
    embedding_list = []
    
    for place_data in all_places_reviews:
        place_name = place_data["place_name"]
        reviews = place_data["reviews"]
        
        for review in reviews:
            for chunk_data in review["chunks"]:
                original_embedding_vector = chunk_data["embedding"]

                # FAISS에 추가하기 위한 형태로 변환 (2D NumPy array)
                embedding = np.array([original_embedding_vector], dtype="float32")
                faiss_index.add(embedding)

                if isinstance(original_embedding_vector, np.ndarray):
                    # NumPy 배열인 경우, Python 리스트로 변환하여 저장 (Langchain 호환성)
                    embedding_list.append(original_embedding_vector)
                else:
                    embedding_list.append(original_embedding_vector)
                
                metadata_store.append({
                    "place_name": place_name,
                    "text": chunk_data["text"],
                    "review_id": review["index"]
                })
    
    print(f"벡터 DB에 총 {len(metadata_store)}개의 청크 저장 완료")

    # FAISS 인덱스, 메타데이터 리스트, 그리고 임베딩 벡터 리스트를 반환
    return faiss_index, metadata_store, embedding_list