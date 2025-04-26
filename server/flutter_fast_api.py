from fastapi import FastAPI
from main import process_category

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/list/{category}")
async def read_list(category: str):
    """
    특정 카테고리에 대한 분석 결과를 반환하는 API 엔드포인트.
    """
    results = await process_category(category)
    return results