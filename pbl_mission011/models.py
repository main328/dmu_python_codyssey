from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base


class Question(Base):
    """
    질문(Question) 정보를 저장하는 SQLAlchemy ORM 모델입니다.
    
    데이터베이스의 'question' 테이블과 매핑됩니다.

    Attributes:
        id (int): 질문의 고유 식별자 (Primary Key).
        subject (str): 질문의 제목. (Nullable=False)
        content (str): 질문의 본문 내용. (Nullable=False)
        create_date (datetime): 질문이 생성된 일시. (Nullable=False)
    """
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)