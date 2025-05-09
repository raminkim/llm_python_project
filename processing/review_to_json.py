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