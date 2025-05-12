from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

import os
import sys

"""

import langchain
import logging # Python 기본 로깅 모듈

try:
    # Langchain의 전역 verbose 모드 활성화
    langchain.globals.set_verbose(True)
    # Langchain의 전역 debug 모드 활성화 (더 상세한 로그)
    langchain.globals.set_debug(True)
    print("정보: Langchain 전역 verbose 및 debug 모드가 활성화되었습니다.")
except Exception as e_global_settings:
    print(f"경고: Langchain 전역 verbose/debug 설정 중 문제 발생: {e_global_settings}")

# Python의 기본 로깅 레벨 설정 (Langchain 로그가 더 잘 보이도록)
# 기본적으로 WARNING 레벨 이상만 출력될 수 있으므로 INFO 또는 DEBUG로 낮춥니다.
try:
    logging.basicConfig(level=logging.INFO)
    # 특정 Langchain 로거의 레벨을 더 낮출 수도 있습니다.
    logging.getLogger("langchain.retrievers.self_query").setLevel(logging.DEBUG)
    # logging.getLogger("langchain").setLevel(logging.DEBUG) # 모든 Langchain 로그를 DEBUG로
    print("정보: Python 로깅 레벨이 INFO로 설정되었고, langchain.retrievers.self_query는 DEBUG로 설정되었습니다.")
except Exception as e_logging_config:
    print(f"경고: Python 로깅 설정 중 문제 발생: {e_logging_config}")
"""


# 프로젝트 루트 디렉토리를 sys.path에 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from config.config import OPENAI_API_KEY

system_prompt = """다음 규칙을 반드시 준수하여 답변하세요.
1. 제공된 문맥만을 기반으로 긍정적인 답변과 부정적인 답변의 비율을 합하여 100%가 되도록 각각 답변합니다.
2. 부정적인 답변에는 '배달을 하지 않음'과 같은 배달 관련 부정적 리뷰를 포함합니다.
3. 다른 답변은 하지 않고, '긍정: n%, 부정: n%' 형식으로 답변합니다.
4. query로 주어진 장소 이름과 일치하는 리뷰만을 참조해 답변하시오.

문맥:
{context}

질문:
{question}
"""

def generate_answer(query: str, vector_store: FAISS, target_place_name: str):
    """
    미리 생성된 Langchain FAISS 벡터 저장소를 사용하여 사용자 질의에 대한 답변을 생성합니다.

    Args:
        query: 사용자의 질문 문자열.
        vector_store: 미리 생성된 Langchain FAISS 벡터 저장소 객체.

    Returns:
        생성된 답변 문자열 또는 오류 메시지.
    """
    
    try:
        # OpenAI LLM 초기화
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0,
            api_key = OPENAI_API_KEY
        )

        promptTemplate = PromptTemplate(
            template = system_prompt,
            input_variables = ["context", "question"]
        )

        chain_type_kwargs = {"prompt": promptTemplate}


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
            search_kwargs = {"k":15, "filter": {"place_name":target_place_name}},
            verbose = True
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm = llm,
            retriever = retriever,
            return_source_documents=True, # 참고한 문서를 확인하기 위해 True로 설정 후 디버깅
            chain_type_kwargs=chain_type_kwargs
        )

        result = qa_chain.invoke({"query": query})

        """
        # --- Retriever가 가져온 리뷰와 장소명 출력 (디버깅) ---
        print("\n==================================================")
        print("🔍 Retriever가 가져온 문서 (리뷰 및 장소 정보):")
        print("==================================================")
        if "source_documents" in result and result["source_documents"]:
            pass
            for i, doc in enumerate(result["source_documents"]):
                place_name = doc.metadata.get("place_name", "장소명 없음")

                review_id = doc.metadata.get("review_id", "ID 없음") # 리뷰 ID가 있다면 출력

                print(f"\n📄 문서 {i+1}:")
                print(f"  📍 장소명  : {place_name}")
                print(target_place_name == place_name)
                print(f"  🆔 리뷰 ID : {review_id}")
                print(f"  📝 내용 (일부):")
                
                # page_content를 적절한 길이로 나누어 여러 줄로 출력
                content = doc.page_content
                # 보기 좋게 80자 단위로 줄바꿈하며, 최대 5줄 (400자) 정도만 출력
                max_lines_to_show = 5
                chars_per_line = 80
                for line_num, j in enumerate(range(0, len(content), chars_per_line)):
                    if line_num >= max_lines_to_show:
                        print(f"     ...")
                        break
                    print(f"     {content[j:j+chars_per_line]}")
                
                print("-" * 50) # 각 문서 구분선
        else:
            print("  검색된 문서가 없습니다.")
            # qa_chain.return_source_documents가 True인지 다시 확인하는 로직 (선택적)
            if not qa_chain.return_source_documents:
                print("  (힌트: RetrievalQA 체인 생성 시 return_source_documents=True 로 설정되어 있는지 확인하세요.)")
        print("==================================================\n")
        # --- 출력 코드 끝 ---

        """


        return result["result"]
    
    except Exception as e:
        # print(f"답변 생성 중 오류 발생: {e}") # 디버깅용
        return f"오류: 답변 생성 중 문제가 발생했습니다. ({e})"