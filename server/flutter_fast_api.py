from fastapi import FastAPI
from main import process_category
import pymysql as sql
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import socket
from starlette.responses import JSONResponse
import time
import threading
import os

load_dotenv()

app = FastAPI()

# 오류 나서 주석 처리

conn = sql.connect(
    host='127.0.0.1',
    user='root',
    password=os.getenv("DB_PASSWORD"),
    database='route_recommendation',
    charset='utf8mb4',
)

cursor = conn.cursor()
hostname = socket.gethostname()
privateIP = 'http://' + socket.gethostbyname(hostname) + ':8000/'

app.add_middleware(
    CORSMiddleware,
    allow_origins=privateIP,  # 허용할 출처
    allow_credentials=True,  # 인증 정보 포함 여부
    allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],  # 허용할 헤더
)

is_connected = False

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #udp 소켓 생성. IPv4
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    #udp 소켓이 브로드캐스트 메시지를 보내도록 설정
def broadcast():
    while not is_connected: 
        udp_socket.sendto(privateIP.encode(), ("255.255.255.255", 8888))
        time.sleep(5)
broadcast_thread = threading.Thread(target=broadcast, daemon=True)
broadcast_thread.start()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/list/{category}")
async def read_list(category: str, x: float, y:float):
    """
    특정 카테고리에 대한 분석 결과를 반환하는 API 엔드포인트.
    """
    start_time = time.time()
    results = await process_category(category, x, y)
    end_time = time.time()
    print(f"총 요청 처리 시간: {end_time-start_time:.2f}")

    return JSONResponse(content=results, media_type="application/json; charset=utf-8")

@app.post("/insert_new_place")
async def insert_new_place(placeName: str, userID: str, startDate: str, endDate: str):
    """
    사용자가 추가한 장소 정보를 DB에 삽입

    Args:
        placeName (str): 장소 이름
        userID (str): 사용자 ID
        startDate (str): 여행 시작 날짜
        endDate (str): 여행 종료 날짜

    Returns:
        _type_: JSON, 장소 정보 추가 여부 반환환
    """
    try:
        cursor.execute("insert into place_list (place_name, id, start_date, end_date)\
                        values (%s, %s, %s, %s)", (placeName, userID, startDate, endDate))
        conn.commit()
        cursor.execute("select * from place_list")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f'error {e}')
        return False

@app.get("/get_user_place")
async def get_user_place(userID: str):
    try:
        print(userID)
        cursor.execute("select * from place_list where id = %s", (userID,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f'error {e}')

@app.post("/insert_user_info")
async def insert_user_info(userID: str, userPW: str):
    """
    회원 가입한 사용자 정보를 DB에 추가

    Args:
        userID (str): 사용자 ID
        userPW (str): SHA256으로 해싱된 사용자 암호

    Returns:
        _type_: _description_
    """
    try:
        print(f'{userID}, {userPW}')
        cursor.execute("insert into users_info (id, password) values (%s, %s)", (userID, userPW))
        conn.commit()
        cursor.execute("select * from users_info")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f'error {e}')

@app.get("/user_validation")
async def user_validation(userID: str, userPW: str):
    """
    사용자 로그인 시 인증

    Args:
        userID (str): 사용자 입력 ID
        userPW (str): 사용자 PW

    Returns:
        _type_: _description_
    """
    try:
        cursor.execute("select id, password from users_info where id = %s and password = %s", (userID, userPW))
        result = cursor.fetchall()
        if not result:
            return False
        else:
            return True
    except Exception as e:
        print(f'uesr validation error {e}')

@app.get("/get_connect_state")
async def get_connect_state():
    """
    플러터 앱과 사설 네트워크 서버에 연결되었는지 확인인

    Returns:
        _type_: _description_
    """
    return JSONResponse(content={"message": "확인"}, media_type="application/json; charset=utf-8")

@app.get("/duplicate_check")
async def checkIdDuplicate(userID: str):
    """
    ID 중복 확인인

    Args:
        userID (str): 사용자 입력 ID

    Returns:
        _type_: _description_
    """
    try:
        isDuplicate = False
        print(userID)
        cursor.execute("select id from users_info where id = %s", (userID,))
        result = cursor.fetchall()
        if result:
            isDuplicate = True
        print(result)
    except Exception as e:
        print(f'error {e}')
    return isDuplicate
