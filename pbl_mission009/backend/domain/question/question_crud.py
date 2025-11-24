from datetime import datetime
from sqlalchemy.orm import Session
from domain.question.question_schema import QuestionCreate
from models import Question


def get_question_list(db: Session) -> list[Question]:
    """
    데이터베이스에서 질문 목록을 조회합니다.
    작성일시(create_date)를 기준으로 내림차순 정렬합니다.

    Args:
        db (Session): 데이터베이스 세션

    Returns:
        list[Question]: 조회된 질문 객체 리스트
    """
    question_list = db.query(Question).order_by(Question.create_date.desc()).all()
    return question_list


def create_question(db: Session, question_create: QuestionCreate) -> None:
    """
    새로운 질문을 데이터베이스에 저장합니다.

    Args:
        db (Session): 데이터베이스 세션
        question_create (QuestionCreate): 저장할 질문 데이터 스키마

    Returns:
        None
    """
    db_question = Question(
        subject=question_create.subject,
        content=question_create.content,
        create_date=datetime.now()
    )
    db.add(db_question)
    db.commit()