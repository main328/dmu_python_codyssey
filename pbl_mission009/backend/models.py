from sqlalchemy import Column, Integer, aString, Text, DateTime
from database import Base


class Question(Base):
    """
    질문(Question) 정보를 저장하는 데이터베이스 테이블 모델입니다.

    Attributes:
        id (int): 질문 고유 번호 (Primary Key)
        subject (str): 질문 제목
        content (str): 질문 내용
        create_date (datetime): 작성 일시
    """
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)