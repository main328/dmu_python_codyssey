import contextlib  # [수행과제] contextlib 임포트
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 현재 파일 위치 기준 .env 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./myapi.db')

if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# [수행과제] contextlib을 사용한 컨텍스트 매니저 정의
@contextlib.contextmanager
def db_conn():
    """
    데이터베이스 세션을 생성하고 종료하는 로직을 담은 컨텍스트 매니저
    """
    db = SessionLocal()
    try:
        print('[INFO] DB 세션 연결 완료.')
        yield db
    finally:
        print('[INFO] DB 세션 연결 종료.')
        db.close()


# [수행과제] 의존성 주입(Dependency Injection)을 위한 함수
def get_db():
    """
    FastAPI Depends에서 사용할 함수.
    위에서 만든 db_conn 컨텍스트 매니저를 실행(with)하여 세션을 반환합니다.
    """
    with db_conn() as db:
        yield db