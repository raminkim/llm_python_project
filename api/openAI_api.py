import asyncio
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
import lark
import os
import traceback



import langchain
import logging # Python 기본 로깅 모듈


# try:
#     # Langchain의 전역 verbose 모드 활성화
#     langchain.globals.set_verbose(True)
#     # Langchain의 전역 debug 모드 활성화 (더 상세한 로그)
#     langchain.globals.set_debug(True)
#     print("정보: Langchain 전역 verbose 및 debug 모드가 활성화되었습니다.")
# except Exception as e_global_settings:
#     print(f"경고: Langchain 전역 verbose/debug 설정 중 문제 발생: {e_global_settings}")



# Python의 기본 로깅 레벨 설정 (Langchain 로그가 더 잘 보이도록)
# 기본적으로 WARNING 레벨 이상만 출력될 수 있으므로 INFO 또는 DEBUG로 낮춥니다.
# try:
#     logging.basicConfig(level=logging.INFO)
#     # 특정 Langchain 로거의 레벨을 더 낮출 수도 있습니다.
#     logging.getLogger("langchain.retrievers.self_query").setLevel(logging.DEBUG)
#     # logging.getLogger("langchain").setLevel(logging.DEBUG) # 모든 Langchain 로그를 DEBUG로
#     print("정보: Python 로깅 레벨이 INFO로 설정되었고, langchain.retrievers.self_query는 DEBUG로 설정되었습니다.")
# except Exception as e_logging_config:
#     print(f"경고: Python 로깅 설정 중 문제 발생: {e_logging_config}")


system_prompt = """다음 규칙을 반드시 준수하여 답변하세요.
1. 제공된 '문맥(실제 방문자 리뷰들)'을 분석하여, 해당 장소에 대한 전반적인 긍정 또는 부정 수준을 **AI score로 평가**합니다.
2. 부정적인 내용에는 '배달을 하지 않음'과 같은 배달 관련 부정적 리뷰를 포함하여 AI score 산정 시 종합적으로 고려합니다.
3. 답변은 반드시 다음 JSON 형식으로만 제공해야 하며, 다른 내용은 일절 포함하지 않습니다:
{{
  "AI_score": 리뷰와 거리를 기반으로 산정된 긍정도 점수(float, 0~10점)
}}
4. '문맥'에 분석할 내용이 있다면, 반드시 그 내용을 기반으로 AI score를 산정해야 합니다.
5. 아래에 주어진 **현재 위치로부터의 거리**({distance:.2f} km) 값을 반드시 활용해야 합니다.
6. 계산된 거리를 AI score에 다음과 같이 반영합니다:
   - **거리 ≤ 1km**: 위치 접근성이 매우 좋음 → 점수에 +0.5~1.0점 가산 여지를 고려  
   - **1km < 거리 ≤ 3km**: 접근성 무난함 → 점수 변화 없음  
   - **거리 > 3km**: 다소 먼 거리 → 점수에 −0.5~1.0점 감점 여지를 고려
7. '질문'에 명시된 장소 이름과 '문맥'에 있는 [장소명 : ...] 부분이 일치하는 리뷰들을 주로 참조합니다.
8. '문맥'이 전혀 제공되지 않았거나, "리뷰 없음"과 같이 분석할 내용이 없는 경우에는 **'AI score': 0** 으로 답변합니다.

AI score 기본 기준:
- **10점**: 리뷰가 압도적으로 긍정적이며, 매우 높은 만족도를 나타내는 경우
- **8점**: 리뷰가 대부분 긍정적이며, 사소한 문제만 존재하는 경우
- **6점**: 전반적으로 긍정적이지만, 명확한 단점이 다수 존재하는 경우
- **4점**: 긍정·부정이 비슷하거나, 종합 불만 요소가 자주 언급되는 경우
- **2점**: 부정 리뷰가 대부분이며, 긍정 요소가 제한적인 경우
- **0점**: 리뷰가 전부 부정적이거나, 분석할 내용이 전혀 없는 경우

다음은 현재 분석 대상 장소의 정보입니다. AI score 산정 시 참고하십시오:
- 장소명: [{place_name}]
- 현재 위치로부터 거리: {distance:.2f} km

문맥:
{context}

질문:
{question}
""".strip()

async def generate_answer(queries: list, vector_store: Chroma):
    """
    미리 생성된 Langchain FAISS 벡터 저장소를 사용하여 사용자 질의에 대한 답변을 생성합니다.

    Args:
        place_query_inputs: 각 장소별 system prompt에 사용될 쿼리, 현재 영업 상태 정보, 영업 상태 정보에 대한 설명(description), 장소 리뷰 평점, 장소 리뷰 수가 들어있는 dictionary.
        vector_store: 미리 생성된 Langchain Chroma 벡터 저장소 객체

    Returns:
        생성된 답변 리스트
    """
    
    try:
        # Gemini LLM 초기화
        llm = ChatGoogleGenerativeAI(
            model = "gemini-2.0-flash",
            temperature = 0,
            api_key = os.getenv("GEMINI_API_KEY")
        )

        document_contents_description = "A collection of user reviews for various places, primarily restaurants and cafes. Each review talks about user experiences, food, service, atmosphere, etc."

        metadata_field_info = [
            AttributeInfo(
                name="place_name",
                description="The **exact name** of the place or restaurant. If the user's query mentions a specific place name like '브릭스피자' or '육림객잔', you **MUST** create a filter where this 'place_name' field **EXACTLY matches** the mentioned place name. Do not include other places if a specific one is named.", # 더 강력하고 명확한 지시 추가
                type="string",
            ),
        ]

        retriever = SelfQueryRetriever.from_llm(
            llm = llm,
            vectorstore = vector_store,
            document_contents = document_contents_description,
            metadata_field_info = metadata_field_info,
            search_kwargs = {"k":20},
            verbose = True
        )

        async def generate_prompt(place_name: str, place_info: dict):

            query = place_info.get('query')

            # query(장소명 포함)과 관련된 documents(리뷰들)을 담은 리스트인 docs.
            docs = await retriever.ainvoke(query)

            # 중복된 page_content를 추적하기 위한 set은 여전히 필요합니다.
            unique_docs_content_for_comp = set()

            # 리스트 컴프리헨션으로 deduplicated_docs 생성
            deduplicated_docs = [
                doc
                for doc in docs
                if doc.page_content not in unique_docs_content_for_comp # 현재 doc.page_content가 아직 unique_docs_content_for_comp에 없으면,
                and not unique_docs_content_for_comp.add(doc.page_content) # unique_docs_content_for_comp에 해당 내용을 추가한다. add는 추가되면 None을 반환하므로 not으로 처리하였다.
            ]

            # 리스트 docs를 통해 "-[장소명] (리뷰)" 형태의 context를 생성한다.
            context = "\n".join(
                f"- [장소명 : {doc.metadata.get('place_name', '알 수 없음')}] {doc.page_content}"
                for doc in deduplicated_docs
            ).strip()

            # 이전에 haversine 패키지를 통해 계산했던 거리를 가져온다.
            distance = place_info.get("distance")

            # system_prompt의 {context}, {question} 자리에 각각 context, query를 넣는다.
            prompt = system_prompt.format(
                place_name = place_name,
                distance = distance,
                context = context,
                question = query
            )

            return prompt

        generate_prompt_tasks = [
            generate_prompt(place_name, place_info)
            for place_name, place_info in queries.items()
        ]
        prompts = await asyncio.gather(*generate_prompt_tasks)

        results = await llm.abatch(prompts)

        return [result.content for result in results]
    
    except Exception as e:
        print(f"답변 생성 중 오류 발생: {e}") # 디버깅용
        print("========== 전체 트레이스백 시작 ==========")
        traceback.print_exc() # 전체 트레이스백을 출력합니다.
        print("========== 전체 트레이스백 끝 ==========")
        return f"오류: 답변 생성 중 문제가 발생했습니다. ({e})"