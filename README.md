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

- **Python  3.10.16** 설치: ([https://www.python.org/downloads/](https://www.python.org/downloads/))
  FastAPI 서버를 실행하기 위한 Python 환경이 필요합니다. 개발에 3.10.16 버전을 사용하여 해당 버전으로 기술하였습니다.

- **pip** (Python 패키지 관리자) 설치: Python 패키지를 설치하고 관리하는 데 사용됩니다. \n Python 설치 시 함께 설치되는 경우가 많습니다.
  - 패키지 설치를 돕는 'package_install' 실행 방법

    1. **실행 권한 부여**  
       ```bash
       chmod +x package_install.sh
       ```
    2. **패키지 설치 스크립트 실행**
        ```bash
         ./lib_install.sh
         ```
    3. **(선택) 가상환경 활성화**<br>
        만약 가상환경을 이미 만들어 두셨다면, ```source .venv/bin/activate```을 주석 해제하세요!

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
  - **AI_score**: Gemini가 판단한 장소 평가 점수 (0 ~ 10)
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
        "store_name": "육림객잔",
        "AI_score": 9.0,
        "x": 127.7415547,
        "y": 37.8742425,
        "status": "영업 종료",
        "status_description": "11:30에 영업 시작",
        "visitorReviewScore": null,
        "visitorReviewCount": "55",
        "phone_number": null
    },
    {
        "store_name": "진미닭갈비 본점",
        "AI_score": 7.5,
        "x": 127.7367503,
        "y": 37.8682037,
        "status": "영업 종료",
        "status_description": "10:30에 영업 시작",
        "visitorReviewScore": "4.46",
        "visitorReviewCount": "807",
        "phone_number": "033-243-2888"
    },
    {
        "store_name": "1.5닭갈비 본점",
        "AI_score": 9.0,
        "x": 127.7531309,
        "y": 37.876346,
        "status": "영업 종료",
        "status_description": "11:00에 영업 시작",
        "visitorReviewScore": "4.46",
        "visitorReviewCount": "3,622",
        "phone_number": "033-253-8635"
    },
    {
        "store_name": "브릭스피자",
        "AI_score": 6.8,
        "x": 127.7464033,
        "y": 37.8724044,
        "status": "영업 종료",
        "status_description": "12:00에 영업 시작",
        "visitorReviewScore": "4.57",
        "visitorReviewCount": "571",
        "phone_number": "033-911-9023"
    },
    {
        "store_name": "중화루",
        "AI_score": 6.5,
        "x": 127.7357583,
        "y": 37.8755742,
        "status": "영업 종료",
        "status_description": "11:00에 영업 시작",
        "visitorReviewScore": "4.39",
        "visitorReviewCount": "665",
        "phone_number": "033-254-2591"
    },
    {
        "store_name": "감미옥",
        "AI_score": 4.5,
        "x": 127.1228405,
        "y": 37.4088281,
        "status": "영업 종료",
        "status_description": "07:00에 영업 시작",
        "visitorReviewScore": "4.22",
        "visitorReviewCount": "4,474",
        "phone_number": "031-709-9448"
    },
    {
        "store_name": "큰집한우",
        "AI_score": 7.5,
        "x": 127.7349257,
        "y": 37.8778518,
        "status": "영업 종료",
        "status_description": "11:00에 영업 시작",
        "visitorReviewScore": "4.5",
        "visitorReviewCount": "2,051",
        "phone_number": "033-241-3944"
    },
    {
        "store_name": "만석식당 강원대점",
        "AI_score": 8.5,
        "x": 127.7444784,
        "y": 37.8733656,
        "status": null,
        "status_description": null,
        "visitorReviewScore": "4.52",
        "visitorReviewCount": "268",
        "phone_number": "033-241-5492"
    },
    {
        "store_name": "죽향",
        "AI_score": 9.5,
        "x": 127.7393785,
        "y": 37.8707938,
        "status": "영업 종료",
        "status_description": "11:00에 영업 시작",
        "visitorReviewScore": "4.45",
        "visitorReviewCount": "371",
        "phone_number": "033-253-9031"
    },
    {
        "store_name": "봉수닭갈비막국수",
        "AI_score": 9.0,
        "x": 127.7435446,
        "y": 37.8735329,
        "status": "영업 중",
        "status_description": "10:10에 라스트오더",
        "visitorReviewScore": "4.44",
        "visitorReviewCount": "256",
        "phone_number": "033-252-8136"
    },
    {
        "store_name": "해안막국수",
        "AI_score": 8.5,
        "x": 127.742416,
        "y": 37.875288,
        "status": "영업 종료",
        "status_description": "11:00에 영업 시작",
        "visitorReviewScore": "4.53",
        "visitorReviewCount": "202",
        "phone_number": "033-253-0427"
    },
    {
        "store_name": "착한곱한우곱창 춘천1호점",
        "AI_score": 8.5,
        "x": 127.7497161,
        "y": 37.877809,
        "status": "영업 종료",
        "status_description": "17:00에 영업 시작",
        "visitorReviewScore": "4.51",
        "visitorReviewCount": "375",
        "phone_number": "033-252-8872"
    },
    {
        "store_name": "214도넛",
        "AI_score": 9.0,
        "x": 127.7402129,
        "y": 37.8745336,
        "status": "영업 종료",
        "status_description": "09:00에 영업 시작",
        "visitorReviewScore": "4.89",
        "visitorReviewCount": "1,139",
        "phone_number": null
    },
    {
        "store_name": "멘시루 춘천점",
        "AI_score": 7.5,
        "x": 127.7454931,
        "y": 37.8728951,
        "status": null,
        "status_description": null,
        "visitorReviewScore": "4.48",
        "visitorReviewCount": "264",
        "phone_number": null
    }
]
```


- API 요청 예시 (postman)<br>
  <img src="https://github.com/user-attachments/assets/7e628208-4e5f-4e5b-a470-9d13268dce6d">

