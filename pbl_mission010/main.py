import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from domain.question import question_router

# 데이터베이스 테이블 생성 (Alembic을 쓰지 않을 경우 임시로 사용 가능)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='화성 기지 연구 기록 시스템',
    description='연구 결과 및 재고 관리를 위한 게시판 API',
    version='1.0.0'
)

# 라우터 등록
app.include_router(question_router.router)

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# 정적 파일 마운트 (CSS, JS 등)
app.mount('/static', StaticFiles(directory=FRONTEND_DIR), name='static')


@app.get('/')
def index():
    """
    메인 페이지 반환
    """
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))