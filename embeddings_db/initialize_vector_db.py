import numpy as np
import faiss

def initialize_vector_db(all_places_reviews):
    """
    모든 장소의 리뷰 데이터를 FAISS 벡터 DB에 저장
    """
    global index, metadata_store
    
    embedding_dim = 1536  # text-embedding-3-small 차원
    index = faiss.IndexFlatL2(embedding_dim)
    
    metadata_store = []
    
    for place_data in all_places_reviews:
        place_name = place_data["place_name"]
        reviews = place_data["reviews"]
        
        for review in reviews:
            for chunk_data in review["chunks"]:
                embedding = np.array([chunk_data["embedding"]], dtype="float32")
                index.add(embedding)
                
                metadata_store.append({
                    "place_name": place_name,
                    "text": chunk_data["text"],
                    "review_id": review["index"]
                })
    
    print(f"벡터 DB에 총 {len(metadata_store)}개의 청크 저장 완료")