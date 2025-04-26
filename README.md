# FastAPI 기반 Flutter 연동 서버 (Python 구현)

## 프로젝트 개요
이 프로젝트는 LLM을 활용한 여행 경로 추천 앱 'TripOut'을 위해 개발된 Python FastAPI 서버입니다.

https://rustic-cave-d05.notion.site/LLM_python_project-1df41e3234ba802a9548d05fea3fc885?pvs=74

## 시작하기

이 섹션에서는 FastAPI 서버를 로컬 환경에서 실행하고 사용하는 방법을 설명합니다.

### 1. 필수 조건

- **Python  3.8 이상** 설치: ([https://www.python.org/downloads/](https://www.python.org/downloads/)) FastAPI 서버를 실행하기 위한 Python 환경이 필요합니다.

- **pip** (Python 패키지 관리자) 설치: Python 패키지를 설치하고 관리하는 데 사용됩니다. Python 설치 시 함께 설치되는 경우가 많습니다.
  - **fastapi**: Web Framework
  - **uvicorn**: ASGI 서버
  - **openAI**: OpenAI Python 라이브러리
  - **requests**: HTTP 요청 라이브러리 (API, REST API 호출에 사용됩니다.)
  - **python-dotenv**: 환경 변수 로드 라이브러리

- **외부 API KEY**: 프로젝트에서 사용하는 외부 API 키가 필요합니다.
  - **OpenAI API KEY**
  - **KakaoMap API KEY**
  - **Naver API KEY**
