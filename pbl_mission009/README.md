.
├── .env                  # [설정] DB 경로 등 보안이 필요한 환경 변수
├── requirements.txt      # [설정] 필요한 파이썬 패키지 목록
├── frontend/             # [화면] 웹 브라우저용 소스 코드
│   └── index.html
└── backend/              # [서버] 핵심 로직 및 API
    ├── main.py           # 앱 실행 진입점 (Entry Point)
    ├── database.py       # 데이터베이스 연결 설정
    ├── models.py         # 데이터베이스 테이블 설계도
    ├── alembic.ini       # 마이그레이션 설정 파일
    ├── migrations/       # 마이그레이션 스크립트 저장소
    └── domain/           # 기능별 로직 분리
        └── question/     # '질문/기록' 관련 기능 모음
            ├── question_schema.py  # 데이터 검증 (Pydantic)
            ├── question_crud.py    # DB 쿼리 실행
            └── question_router.py  # API URL 연결



pip install -r requirements.txt


1. 모델 정의 (models.py):

새로운 테이블 클래스를 작성합니다. (class Answer(Base): ...)

2. 마이그레이션 생성 (Alembic):

alembic revision --autogenerate -m "메시지" 명령어로 변경 사항을 기록합니다.

alembic upgrade head 명령어로 DB에 반영합니다.

3. 스키마 작성 (schema.py):

입력받을 데이터와 출력할 데이터의 형식을 정의합니다.

4. CRUD 작성 (crud.py):

데이터를 저장(add)하거나 조회(query)하는 함수를 만듭니다.

5. 라우터 등록 (router.py):

URL과 CRUD 함수를 연결합니다.