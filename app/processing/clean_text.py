import re

def clean_text(text: str) -> str:
    # 입력값이 문자열인지 확인
    if not isinstance(text, str):
        text = str(text)  # 문자열로 변환
    text = re.sub(r"[^\w\s가-힣]", " ", text)  # 특수문자 및 이모지 제거
    text = re.sub(r"\s+", " ", text).strip()  # 공백 정리
    return text