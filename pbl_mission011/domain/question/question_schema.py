import datetime
from pydantic import BaseModel, field_validator


class QuestionCreate(BaseModel):
    """
    질문 생성(Create) 요청 시 클라이언트로부터 전달받는 데이터 구조(DTO)입니다.

    Attributes:
        subject (str): 등록할 질문의 제목.
        content (str): 등록할 질문의 내용.
    """
    subject: str
    content: str

    @field_validator('subject', 'content')
    def not_empty(cls, v: str) -> str:
        """
        문자열 필드에 빈 값이나 공백만 있는 경우를 방지하는 검증 로직입니다.

        Args:
            v (str): 검증할 필드의 값.

        Returns:
            str: 검증이 통과된 값 (좌우 공백 제거 등 필요 시 전처리 가능).

        Raises:
            ValueError: 값이 없거나 공백으로만 이루어진 경우 발생.
        """
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


class Question(BaseModel):
    """
    클라이언트에게 응답(Response)으로 반환할 질문 데이터 구조입니다.

    Attributes:
        id (int): 질문 ID.
        subject (str): 질문 제목.
        content (str): 질문 내용.
        create_date (datetime.datetime): 생성 일시.
    """
    id: int
    subject: str
    content: str
    create_date: datetime.datetime

    class Config:
        """
        Pydantic 설정 클래스.
        
        Attributes:
            from_attributes (bool): True일 경우, ORM 객체(SQLAlchemy 모델)를 
                                    Pydantic 모델로 자동 변환하는 것을 허용합니다.
        """
        from_attributes = True
        # from_attributes = False