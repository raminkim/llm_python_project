# FastAPI 기반 Flutter 연동 서버 (Python 구현)

# 프로젝트 소개

이 프로젝트는 **LLM**을 활용한 여행 경로 추천 앱 '**TripOut**'을 위한 Python FastAPI 서버입니다.

- [TripOut FastAPI Backend Docs 페이지 바로가기](https://rustic-cave-d05.notion.site/LLM_python_project-1df41e3234ba802a9548d05fea3fc885?pvs=74)

---

## 📅 개발 기간

- **2025.03.29(토) ~ (진행 중)**

---

## 💻 개발 환경

- **Python**: 3.10.16
- **Framework**: FastAPI 0.115.12
- **IDE**: Visual Studio Code
- **Web Server (ASGI)**: Uvicorn

---

## 🚀 시작하기

FastAPI 서버를 로컬 환경에서 실행하는 방법을 안내합니다.

### 1. 필수 조건

- **Python 3.10.16**  
  [공식 다운로드 링크](https://www.python.org/downloads/)  
  (개발은 3.10.16 버전 기준입니다.)

- **pip**  
  Python 패키지 관리자. 대부분 Python 설치 시 자동 포함됩니다.

- **외부 API KEY**  
    - OpenAI API KEY  
    - KakaoMap API KEY  
    - Naver API KEY

- **패키지 설치 스크립트(`package_install.sh`) 사용법**
    1. **실행 권한 부여**
        ```bash
        chmod +x package_install.sh
        ```
    2. **패키지 설치 (Windows의 경우, Git Bash 등에서 실행)**
        ```bash
        ./package_install.sh
        ```
    3. **(선택) 가상환경 활성화**
        - 이미 가상환경이 있다면 아래 명령어를 실행하세요.
            ```bash
            source .venv/bin/activate
            ```

- **외부 API KEY**: 프로젝트에서 사용하는 외부 API 키가 필요합니다.
  - **OpenAI API KEY**
  - **KakaoMap API KEY**
  - **Gemini API KEY**

### 2. 환경 변수 세팅

1. **환경 변수 파일 생성**  
    `env_sample` 파일을 복사해서 `.env` 파일로 이름을 변경하세요.

2. **.env 파일 편집**  
    필요한 API KEY 값을 `.env`에 입력합니다.

---

### 3. FastAPI 서버 실행

아래 명령어로 서버를 실행하세요:

```bash
uvicorn app.fastapi_cicd.flutter_fast_api:app --reload --host=0.0.0.0 --port 8000
```

### 4. 특정 좌표 주변 카테고리 장소 리뷰 분석 API 가이드

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


### 5. 📋커밋 컨벤션
프로젝트의 일관성을 위해 다음 커밋 컨벤션을 사용합니다.

##### 🏷️ 커밋 타입
| Tag         | Name           | Description                                      |
|-------------|----------------|--------------------------------------------------|
| Feat        | 기능 추가      | 새로운 기능/주요 파일을 추가할 때                         |
| Fix         | 버그 수정      | 버그를 수정할 때                                |
| Design      | 디자인 변경    | CSS 등 사용자 UI 디자인 변경                    |
| !BREAKING CHANGE | API 변경   | 커다란 API 변경의 경우                          |
| !HOTFIX     | 긴급 버그      | 급하게 치명적인 버그를 고칠 때                  |
| Style       | 스타일링       | 코드 포맷 변경, 세미콜론 누락, 코드 변경 없음   |
| Refactor    | 리팩토링       | 프로덕션 코드 리팩토링                          |
| Comment     | 주석           | 필요한 주석 추가 및 변경                        |
| Docs        | 문서           | 문서 수정                                       |
| Test        | 테스트         | 테스트 코드 추가/리팩토링(Production Code 변경 없음) |
| Chore       | 잡무           | 빌드 업무, 패키지 매니저 수정 등 (코드 변경 없음)|
| Rename      | 이름 변경      | 파일/폴더명 수정 또는 이동만 수행한 경우        |
| Remove      | 삭제           | 파일 삭제 작업만 수행한 경우                    |

##### 📝 커밋 메시지 작성 형식
- **타입**: 위 표의 Tag 중 하나
- **간단한 설명**: 50자 이내, 현재형으로 작성
- **상세 설명**: 필요 시 한 줄 띄우고 자세히 작성

##### 💡 커밋 작성 가이드

- **간단한 코드 수정**
    - 버그 수정 → `Fix`
    - 코드 개선 → `Refactor`
    - 포맷팅만 → `Style`
    - 주석 추가 → `Comment`
    - 문서 파일 추가 → `Docs`
- **커밋 메시지는 현재형으로 작성**
- **제목은 50자 이내로 간결하게**
- **본문이 필요한 경우 한 줄 띄우고 상세 설명 작성**