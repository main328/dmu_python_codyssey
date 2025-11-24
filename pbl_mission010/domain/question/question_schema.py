import datetime
from pydantic import BaseModel, field_validator


class QuestionCreate(BaseModel):
    """
    질문 생성 시 클라이언트로부터 입력받는 데이터 구조입니다.
    """
    subject: str
    content: str

    @field_validator('subject', 'content')
    def not_empty(cls, v):
        """빈 문자열이 들어오지 않도록 검증합니다."""
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


class Question(BaseModel):
    """
    클라이언트에게 응답으로 보낼 질문 데이터 구조입니다.
    """
    id: int
    subject: str
    content: str
    create_date: datetime.datetime

    class Config:
        # ORM 객체(SQLAlchemy 모델)를 Pydantic 모델로 자동 변환 허용
        from_attributes = True