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
    2. **패키지 설치 스크립트 실행 (windows의 경우, git bash에서 실행)**
        ```bash
         ./package_install.sh
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


### 특정 좌표 주변 카테고리 장소 리뷰 분석 API 가이드

> 카테고리 종류는 [카카오 지도 API 카테고리 코드](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-category-request-query-category-group-code)를 참고하세요.


##### Request Syntax
- **HTTP Method:** `POST`
- **Endpoint:** `/list/{category}`
- **Content-Type:** `application/json`
- **좌표 데이터:** 쿼리 파라미터로 전달 (`x`, `y`)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"x": 127.743288, "y": 37.872316}' \
  'http://127.0.0.1:8000/list/FD6'
```

##### Request Elements
| Parameter | Type  | Description        |
| --------- | ----- | ------------------ |
| `x`       | float | 경도 (예: 127.743288) |
| `y`       | float | 위도 (예: 37.872316)  |

##### Response Elements
| Key                  | Type   | 설명                                |
| -------------------- | ------ | --------------------------------- |
| `store_name`         | string | 장소 이름                             |
| `AI_score`           | float  | Gemini가 판단한 장소 평가 점수 (0\~10)      |
| `x`                  | float  | 장소의 x좌표(경도)                       |
| `y`                  | float  | 장소의 y좌표(위도)                       |
| `status`             | string | 장소의 현재 영업 정보 (예: '영업 중', '영업 종료') |
| `status_description` | string | 장소의 영업 설명 (예: '11:00에 영업 시작')     |
| `visitorReviewScore` | string | 리뷰 평점(없으면 null)                   |
| `visitorReviewCount` | string | 리뷰 수(없으면 null)                    |
| `phone_number`       | string | 장소 전화번호(없으면 null)                 |

##### Response Example (200 OK)
```json
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
  // ... 이하 생략
]
```

##### 참고사항
- AI_score: Google Gemini 모델이 리뷰/영업정보 등을 종합 평가한 점수 (0~10, 높을수록 추천)

- status/status_description: 실시간 크롤링된 영업 정보(없으면 null)

- visitorReviewScore/visitorReviewCount: 리뷰 평점 및 리뷰 수 (없으면 null)

- phone_number: 장소 연락처(없으면 null)

##### API 요청 예시 (postman)<br>
  <img src="https://github.com/user-attachments/assets/7e628208-4e5f-4e5b-a470-9d13268dce6d">

