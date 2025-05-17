# FastAPI 기반 Flutter 연동 서버 (Python 구현)

##  프로젝트 소개
이 프로젝트는 LLM을 활용한 여행 경로 추천 앱 'TripOut'을 위해 개발된 Python FastAPI 서버입니다.

<a href = "https://rustic-cave-d05.notion.site/LLM_python_project-1df41e3234ba802a9548d05fea3fc885?pvs=74">프로젝트 파일 구조</a>

## 📅 만든 기간
- 2025.03.29(토) ~ 
  
## 💻 개발 환경
- **Python Version**: 3.10.16
- **Framework**: FastAPI Version 0.115.12
- **IDE**: Visual Studio Code
- **Web Server (ASGI)**: Uvicorn

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
  - **langchain_community**
  - **langchain_openai**
  - **langchain_chroma**
  - **pymysql**

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
uvicorn server.flutter_fast_api:app --reload --host=0.0.0.0 --port 8000
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
  - **store_name**: 장소 이름
  - **AI_score**: Gemini가 판단한 장소 평가 점수 (0 ~ 100)
  - **x**: 장소의 x 좌표
  - **y**: 장소의 y 좌표
  - **status**: 장소의 현재 영업 정보 (영업 전 / 영업 중 / 영업 종료, etc). 없다면 null.
  - **status_description**: 장소의 영업 설명. 없다면 null.
  - **visitorReviewScore**: 장소의 리뷰 평점. 없다면 null.
  - **visitorReviewCoun**t: 장소의 리뷰 수. 없다면 null.
  - **phone_number**: 장소의 전화번호. 없다면 null.
```bash
  [
    {
        "store_name": "포지티브즈",
        "AI_score": 98,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "12:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "342",
        "phone_number": null
    },
    {
        "store_name": "스타벅스 강원대점",
        "AI_score": 95,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "09:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "3,186",
        "phone_number": "1522-3232"
    },
    {
        "store_name": "카페 예담더갤러리",
        "AI_score": 95,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "10:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "337",
        "phone_number": null
    },
    {
        "store_name": "이스케이프존 강원대1호점",
        "AI_score": null,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "곧 영업 종료",
        "status_description": "24:00에 영업 종료",
        "visitorReviewScore": null,
        "visitorReviewCount": "42",
        "phone_number": "033-251-6833"
    },
    {
        "store_name": "위위",
        "AI_score": 98,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "12:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "113",
        "phone_number": "070-4216-4516"
    },
    {
        "store_name": "할리스 춘천강원대점",
        "AI_score": 50,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 중",
        "status_description": "06:00에 브레이크타임",
        "visitorReviewScore": null,
        "visitorReviewCount": "98",
        "phone_number": "033-253-0425"
    },
    {
        "store_name": "프롬마인드",
        "AI_score": 99,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "08:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "2,378",
        "phone_number": null
    },
    {
        "store_name": "스타벅스 춘천후석로DT점",
        "AI_score": 85,
        "x": 127.7487156850901,
        "y": 37.88249358099619,
        "status": "영업 종료",
        "status_description": "07:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "240",
        "phone_number": "1522-3232"
    },
    {
        "store_name": "메가MGC커피 강원대점",
        "AI_score": 85,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 중",
        "status_description": "01:00에 영업 종료",
        "visitorReviewScore": null,
        "visitorReviewCount": "561",
        "phone_number": null
    },
    {
        "store_name": "시실리아 커피로스팅 하우스",
        "AI_score": 98,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "12:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "155",
        "phone_number": "070-7768-9255"
    },
    {
        "store_name": "아글라오네마",
        "AI_score": null,
        "x": 127.7487156850901,
        "y": 37.88249358099619,
        "status": "영업 종료",
        "status_description": "12:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "170",
        "phone_number": null
    },
    {
        "store_name": "MST",
        "AI_score": 98,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "11:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "181",
        "phone_number": null
    },
    {
        "store_name": "빈티지다락방",
        "AI_score": 65,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 중",
        "status_description": "01:00에 영업 종료",
        "visitorReviewScore": null,
        "visitorReviewCount": "99",
        "phone_number": "033-6293-4253"
    },
    {
        "store_name": "쿠프만153",
        "AI_score": 95,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 중",
        "status_description": "02:00에 영업 종료",
        "visitorReviewScore": null,
        "visitorReviewCount": "243",
        "phone_number": null
    },
    {
        "store_name": "퍼스트러브",
        "AI_score": null,
        "x": 127.7353546951689,
        "y": 37.87263513844341,
        "status": "영업 종료",
        "status_description": "10:00에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "22",
        "phone_number": null
    }
]
```


- API 요청 예시 (postman)<br>
  <img src="https://github.com/user-attachments/assets/7e628208-4e5f-4e5b-a470-9d13268dce6d">

