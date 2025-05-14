# FastAPI 기반 Flutter 연동 서버 (Python 구현)

## 프로젝트 개요
이 프로젝트는 LLM을 활용한 여행 경로 추천 앱 'TripOut'을 위해 개발된 Python FastAPI 서버입니다.

<a href = "https://rustic-cave-d05.notion.site/LLM_python_project-1df41e3234ba802a9548d05fea3fc885?pvs=74">프로젝트 파일 구조</a>

## 시작하기

이 섹션에서는 FastAPI 서버를 로컬 환경에서 실행하고 사용하는 방법을 설명합니다.

### 1. 필수 조건

- **Python  3.10.6** 설치: ([https://www.python.org/downloads/](https://www.python.org/downloads/))
  FastAPI 서버를 실행하기 위한 Python 환경이 필요합니다. 개발에 3.10.6 버전을 사용하여 해당 버전으로 기술하였습니다.

- **pip** (Python 패키지 관리자) 설치: Python 패키지를 설치하고 관리하는 데 사용됩니다. \n Python 설치 시 함께 설치되는 경우가 많습니다.
  - **fastapi**: Web Framework
  - **uvicorn**: ASGI 서버
  - **openAI**: OpenAI Python 라이브러리
  - **requests**: HTTP 요청 라이브러리 (API, REST API 호출에 사용됩니다.)
  - **python-dotenv**: 환경 변수 로드 라이브러리
  - **lark**

- **외부 API KEY**: 프로젝트에서 사용하는 외부 API 키가 필요합니다.
  - **OpenAI API KEY**
  - **KakaoMap API KEY**
  - **Naver API KEY**


## 실행 방법
### 1. 세팅

(1) **환경 변수 파일 생성** : env_sample 파일을 복사해 .env 파일로 이름을 변경

(2) **.env 파일의 API 키 채우기**

### 2. 서버 실행 방법
```bash
uvicorn server.flutter_fast_api:app --reload
```

### 3. 서버 종료 방법
`ctrl + c`


## API 사용 방법 및 결과 예시
### 특정 좌표 주변 특정 카테고리 장소의 리뷰 분석 요청 (POST)
<a href = "https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-category-request-query-category-group-code"> 카테고리 종류 참고</a>

<p>다음 `curl` 명령어는 <b>`POST` 메소드를 사용</b>하여 <b>`/list/{category}` 엔드포인트</b>에 요청합니다.<br>
<b>좌표 데이터(`x`, `y`)는 **쿼리 파라미터** 형태로 URL에 포함되어 전송됩니다.</b><br>
<b>요청 데이터의 형식은 `application/json`으로 지정되었지만, 실제 좌표 값은 URL을 통해 전달됩니다.</b></p>


- 요청 예시
```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"x": 127.743288, "y": 37.872316}' \
    '[http://127.0.0.1:8000/list/FD6](http://127.0.0.1:8000/list/FD6)'
```

- 응답 예시
```bash
  [
    {
        "store_name": "육림객잔",
        "positive_rate": 90,
        "negative_rate": 10
    },
    {
        "store_name": "진미닭갈비 본점",
        "positive_rate": 85,
        "negative_rate": 15
    },
    {
        "store_name": "1.5닭갈비 본점",
        "positive_rate": 80,
        "negative_rate": 20
    },
        ... (중략)
    {
        "store_name": "돌다리야채곱창",
        "positive_rate": 80,
        "negative_rate": 20
    },
    {
        "store_name": "단하비",
        "positive_rate": 95,
        "negative_rate": 5
    }
]
```


- API 요청 예시 (postman)
  <img src="https://github.com/user-attachments/assets/7e628208-4e5f-4e5b-a470-9d13268dce6d">

