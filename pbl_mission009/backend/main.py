import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from domain.question import question_router

app = FastAPI(
    title='화성 기지 연구 기록 시스템',
    description='연구 결과 및 재고 관리를 위한 게시판 API',
    version='1.0.0'
)

app.include_router(question_router.router)

# 현재 파일(main.py) 기준으로 frontend 폴더의 절대 경로 계산
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

# 정적 파일 경로 설정
app.mount('/static', StaticFiles(directory=FRONTEND_DIR), name='static')


@app.get('/')
def index():
    """
    메인 페이지 반환
    backend 폴더 밖의 frontend/index.html을 찾아 반환합니다.
    """
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))