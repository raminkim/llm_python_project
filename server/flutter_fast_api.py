from fastapi import FastAPI
from main import process_category
import pymysql as sql
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import socket
import time
import threading
import os

load_dotenv()  # .env 파일 로드

is_connected = False
hostname = socket.gethostname()
privateIP = 'http://' + socket.gethostbyname(hostname) + ':8000/'
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #udp 소켓 생성. IPv4
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    #udp 소켓이 브로드캐스트 메시지를 보내도록 설정
def broadcast():
    while not is_connected:
        print("send broadcast message")
        udp_socket.sendto(privateIP.encode(), ("255.255.255.255", 8888))
        time.sleep(5)
broadcast_thread = threading.Thread(target=broadcast, daemon=True)
broadcast_thread.start()
print(privateIP)
app = FastAPI()
conn = sql.connect(
    host='127.0.0.1',
    user='root',
    password=os.getenv("DB_PASSWORD"),
    database='route_recommendation',
    charset='utf8mb4',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cursor = conn.cursor()


# 오류 나서 주석 처리

# conn = sql.connect(
#     host='127.0.0.1',
#     user='root',
#     password=os.getenv("DB_PASSWORD"),
#     database='route_recommendation',
#     charset='utf8mb4',
# )
# origins = [
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # 허용할 출처
#     allow_credentials=True,  # 인증 정보 포함 여부
#     allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST 등)
#     allow_headers=["*"],  # 허용할 헤더
# )

# cursor = conn.cursor()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/list/{category}")
async def read_list(category: str, x: float, y:float):
    """
    특정 카테고리에 대한 분석 결과를 반환하는 API 엔드포인트.
    """
    results = await process_category(category, x, y)
    return results

@app.post("/insert_user_info")
async def insert_user_info(userID: str, userPW: str):
    # try:
    #     print(f'{userID}, {userPW}')
    #     cursor.execute(f"insert into users_info (id, password) values ('{userID}', '{userPW}')")
    #     conn.commit()
    #     cursor.execute("select * from users_info")
    #     result = cursor.fetchall()
    #     conn.close()
    # except Exception as e:
    #     print(f'error {e}')
    # finally:
    #     print(result)
    # return result

    pass

@app.get("/get_connect_state")
async def get_connect_state():
    global is_connected
    is_connected = True
    return {"message": "OK"}

@app.get("/duplicate_check")
async def checkIdDuplicate(userID: str):
    # try:
    #     isDuplicate = False
    #     print(userID)
    #     cursor.execute(f"select id from users_info where id = '{userID}'")
    #     result = cursor.fetchall()
    #     if result:
    #         isDuplicate = True
    #     print(result)
    # except Exception as e:
    #     print(f'error {e}')
    # return isDuplicate
    pass

@app.get("/user_info/")
async def get_user_info():
    return
