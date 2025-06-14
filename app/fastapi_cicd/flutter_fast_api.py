from fastapi import FastAPI, Request
from app.main import process_category
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.responses import JSONResponse
import os
import time
import threading
import socket
import pymysql as sql

load_dotenv()

app = FastAPI()

def is_cloud_run():
    return os.getenv("K_SERVICE") is not None  # Cloud Run 환경 변수

# 환경에 따라 privateIP 분기 처리 및 DB 연결
if is_cloud_run():
    privateIP = os.getenv("SERVICE_URL", "https://your-cloud-run-url.run.app/")

    conn = sql.connect(
        unix_socket=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4"
    )
else:
    try:
        hostname = socket.gethostname()
        privateIP = f"http://{socket.gethostbyname(hostname)}:8000/"
    except Exception:
        privateIP = "http://127.0.0.1:8000/"

    conn = sql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset='utf8mb4',
    )

cursor = conn.cursor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[privateIP],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

is_connected = False
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def broadcast():
    while True:
        udp_socket.sendto(privateIP.encode(), ("255.255.255.255", 8888))
        time.sleep(5)

broadcast_thread = threading.Thread(target=broadcast, daemon=True)
broadcast_thread.start()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/list/{category}")
async def read_list(category: str, x: float, y: float):
    start_time = time.time()
    results = await process_category(category, x, y)
    end_time = time.time()
    print(f"총 요청 처리 시간: {end_time - start_time:.2f}")
    return JSONResponse(content=results, media_type="application/json; charset=utf-8")

@app.post("/insert_new_place")
async def insert_new_place(placeName: str, userID: str, startDate: str, endDate: str):
    try:
        cursor.execute("""insert into place_list (place_name, id, start_date, end_date)
                          values (%s, %s, %s, %s)""", (placeName, userID, startDate, endDate))
        conn.commit()
        cursor.execute("select place_list_id from place_list where id = %s order by place_list_id desc limit 1", userID)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f'error {e}')
        return False

@app.get("/get_user_place")
async def get_user_place(userID: str):
    try:
        cursor.execute("select * from place_list where id = %s", (userID,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f'error {e}')

@app.post("/insert_place_info")
async def insert_place_info(request: Request):
    data = await request.json()
    cursor.execute("""insert into place_info (place_list_id, place_name, x, y, ai_score, phone_number, order_index, day)
                      values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                   (data["placeListID"], data["placeName"], data["x"], data["y"], data["aiScore"], data["phoneNumber"], data["order"], data["day"]))
    conn.commit()
    cursor.execute("select * from place_info where place_list_id = %s", data["placeListID"])
    result = cursor.fetchall()
    return result

@app.get("/get_place_info")
async def get_place_info(placeListID: int):
    cursor.execute("select * from place_info where place_list_id=%s", placeListID)
    result = cursor.fetchall()
    return result

@app.post("/init_place_info")
async def init_place_info(placeListID: int):
    cursor.execute("delete from place_info where place_list_id=%s", placeListID)

@app.post("/delete_place_list")
async def delete_place_list(placeListID: int):
    cursor.execute("delete from place_list where place_list_id=%s", (placeListID,))
    conn.commit()
    return "{message: OK}"

@app.post("/insert_user_info")
async def insert_user_info(userID: str, userPW: str):
    try:
        cursor.execute("insert into users_info (id, password) values (%s, %s)", (userID, userPW))
        conn.commit()
        cursor.execute("select * from users_info")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f'error {e}')

@app.get("/user_validation")
async def user_validation(userID: str, userPW: str):
    try:
        cursor.execute("select id, password from users_info where id = %s and password = %s", (userID, userPW))
        result = cursor.fetchall()
        return bool(result)
    except Exception as e:
        print(f'user validation error {e}')

@app.get("/get_connect_state")
async def get_connect_state():
    return JSONResponse(content={"message": "확인"}, media_type="application/json; charset=utf-8")

@app.get("/duplicate_check")
async def checkIdDuplicate(userID: str):
    try:
        cursor.execute("select id from users_info where id = %s", (userID,))
        result = cursor.fetchall()
        return bool(result)
    except Exception as e:
        print(f'error {e}')
        return False