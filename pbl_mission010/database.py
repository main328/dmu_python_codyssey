import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 현재 파일(database.py)의 위치를 기준으로 .env 파일을 로드합니다.
# 일반적으로 .env는 프로젝트 루트에 위치하므로 경로를 조정합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 환경 변수 로드 (기본값: 로컬 SQLite)
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./myapi.db')

# SQLite 사용 시 스레드 체크 옵션 해제 필요
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    데이터베이스 세션 생성기 (Dependency Injection용)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()