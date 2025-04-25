from openai import OpenAI

system_prompt = """다음 규칙을 반드시 준수하여 답변하세요.
1. 제공된 문맥만을 기반으로 긍정적인 답변과 부정적인 답변의 비율을 합하여 100%가 되도록 각각 답변합니다.
2. 부정적인 답변에는 '배달을 하지 않음'과 같은 배달 관련 부정적 리뷰를 포함합니다.
3. 다른 답변은 하지 않고, '긍정: n%, 부정: n%' 형식으로 답변합니다."""

def generate_answer(client: OpenAI, query, place_data):
    
    place_name = place_data["place_name"]
    review_jsons = place_data["reviews"]
    
    # 해당 장소의 청크 데이터만 추출
    relevant_chunks = []
    for review in review_jsons:
        for chunk_data in review["chunks"]:
            relevant_chunks.append({
                "text": chunk_data["text"],
                "review_id": review["index"]
            })
    
    # 청크 데이터를 문맥으로 결합
    context = "\n\n".join([chunk["text"] for chunk in relevant_chunks[:10]])  # 최대 10개 청크 사용
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{place_name}에 대한 다음 리뷰들을 분석하여 장점, 단점을 요약하고 긍정/부정 비율을 알려주세요:\n\n{context}"}
        ],
        temperature=0.3,
        max_tokens=300
    )
    
    return completion.choices[0].message.content