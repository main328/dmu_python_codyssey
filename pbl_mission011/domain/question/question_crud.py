from datetime import datetime
from sqlalchemy.orm import Session
from domain.question.question_schema import QuestionCreate
from models import Question


def get_question_list(db: Session) -> list[Question]:
    question_list = db.query(Question).order_by(Question.create_date.desc()).all()
    return question_list


def create_question(db: Session, question_create: QuestionCreate) -> None:
    db_question = Question(
        subject=question_create.subject,
        content=question_create.content,
        create_date=datetime.now()
    )
    db.add(db_question)
    db.commit()