import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from domain.question import question_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='화성 기지 연구 기록 시스템',
    description='연구 결과 및 재고 관리를 위한 게시판 API',
    version='1.0.0'
)

app.include_router(question_router.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app.mount('/static', StaticFiles(directory=FRONTEND_DIR), name='static')


@app.get('/')
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))