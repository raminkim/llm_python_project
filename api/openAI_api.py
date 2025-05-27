import asyncio
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


# TODO: 거리 추가, AI score 추가
system_prompt = """다음 규칙을 반드시 준수하여 답변하세요.
1. 제공된 '문맥(실제 방문자 리뷰들)'을 분석하여, 해당 장소에 대한 전반적인 긍정 또는 부정 수준을 **AI Score로 평가**합니다.
2. 부정적인 내용에는 '배달을 하지 않음'과 같은 배달 관련 부정적 리뷰를 포함하여 AI score 산정 시 종합적으로 고려합니다.
3. 다른 답변은 하지 않고, **'AI score: n점'** 형식으로 답변합니다. (점수는 0점에서 100점 사이이며, 높을수록 긍정적인 평가를 의미합니다.)
4. '문맥'에 분석할 내용이 있다면, 반드시 그 내용을 기반으로 AI Score를 산정해야 합니다.
    a. AI Score는 주로 **'문맥'에서 파악된 긍정적 내용의 비중과 만족도**를 반영하여 0~100점으로 결정합니다.
    b. 아래 제공되는 '방문자 리뷰 평점'은 '문맥'의 내용이 매우 제한적이거나 해석이 모호할 경우, AI score 산정에 **참고할 수 있는 보조적인 정보**로 활용합니다. 단, '문맥'에서 명확히 드러나는 내용이 있다면 '문맥'의 내용을 우선으로 합니다.
5. '질문'에 명시된 장소 이름과 '문맥'에 있는 [장소명 : ...] 부분이 일치하는 리뷰들을 주로 참조하여 답변합니다. (이는 아래 '현재 분석 대상 장소 정보'의 장소명과도 일치해야 합니다.)
6. '문맥'이 전혀 제공되지 않았거나, "리뷰 없음"과 같이 분석할 내용이 없는 경우에는 **'AI score: 0점'** 으로 답변합니다.

다음은 현재 분석 대상 장소의 정보입니다. AI score 산정 시 아래 정보를 참고하십시오:
- 장소명: [{place_name}]

문맥:
{context}

질문:
{question}
""".strip()

async def generate_answer(queries: list, vector_store: FAISS):
    """
    미리 생성된 Langchain FAISS 벡터 저장소를 사용하여 사용자 질의에 대한 답변을 생성합니다.

    Args:
        place_query_inputs: 각 장소별 system prompt에 사용될 쿼리, 현재 영업 상태 정보, 영업 상태 정보에 대한 설명(description), 장소 리뷰 평점, 장소 리뷰 수가 들어있는 dictionary.
        vector_store: 미리 생성된 Langchain FAISS 벡터 저장소 객체

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
            visitorReviewScore = place_info.get('visitorReviewScore', 'N/A') # 장소 리뷰 평점
            visitorReviewCount = place_info.get('visitorReviewCount', 'N/A') # 장소 리뷰 수

            # query(장소명 포함)과 관련된 documents(리뷰들)을 담은 리스트인 docs.
            docs = await retriever.ainvoke(query)

            # 리스트 docs를 통해 "-[장소명] (리뷰)" 형태의 context를 생성한다.
            context = "\n".join(
                f"- [장소명 : {doc.metadata.get('place_name', '알 수 없음')}] {doc.page_content}"
                for doc in docs
            ).strip()

            # 리뷰 평점, 리뷰 수에 대해 별점 = 4.52 점(리뷰 268개 기반)과 같은 문구를 포함한 문자열
            review_info = f"리뷰 평점 = {visitorReviewScore} 점(리뷰 {visitorReviewCount} 개)"

            # system_prompt의 {context}, {question} 자리에 각각 context, query를 넣는다.
            prompt = system_prompt.format(
                place_name = place_name,
                context = context,
                question = query
            )

            with open('output.txt', 'a', encoding='utf-8') as f:
                f.write(prompt)
                f.write("="*40)
            return prompt

        generate_prompt_tasks = [
            generate_prompt(place_name, place_info)
            for place_name, place_info in queries.items()
        ]
        prompts = await asyncio.gather(*generate_prompt_tasks)

        # print(prompts)
        results = await llm.abatch(prompts)
        # print(f"답변 결과: {results}")

    

        # if "source_documents" in result and result["source_documents"]:
        #     for i, doc in enumerate(result["source_documents"]):
        #         place_name = doc.metadata.get("place_name", "장소명 없음")

        #         review_id = doc.metadata.get("review_id", "ID 없음") # 리뷰 ID가 있다면 출력

        #         print(f"\n📄 문서 {i+1}:")
        #         print(f"  📍 장소명  : {place_name}")
        #         print(target_place_name == place_name)
        #         print(f"  🆔 리뷰 ID : {review_id}")
        #         print(f"  📝 내용 (일부):")
                
        #         # page_content를 적절한 길이로 나누어 여러 줄로 출력
        #         content = doc.page_content
        #         # 보기 좋게 80자 단위로 줄바꿈하며, 최대 5줄 (400자) 정도만 출력
        #         max_lines_to_show = 5
        #         chars_per_line = 80
        #         for line_num, j in enumerate(range(0, len(content), chars_per_line)):
        #             if line_num >= max_lines_to_show:
        #                 print(f"     ...")
        #                 break
        #             print(f"     {content[j:j+chars_per_line]}")
                
        #         print("-" * 50) # 각 문서 구분선
        # else:
        #     print("  검색된 문서가 없습니다.")
        # print("==================================================\n")
        # --- 출력 코드 끝 ---

    


        return [result.content for result in results]
    
    except Exception as e:
        print(f"답변 생성 중 오류 발생: {e}") # 디버깅용
        print("========== 전체 트레이스백 시작 ==========")
        traceback.print_exc() # 전체 트레이스백을 출력합니다.
        print("========== 전체 트레이스백 끝 ==========")
        return f"오류: 답변 생성 중 문제가 발생했습니다. ({e})"