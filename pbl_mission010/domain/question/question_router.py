from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from domain.question import question_schema, question_crud

router = APIRouter(
    prefix='/api/question',
)


@router.get('/list', response_model=list[question_schema.Question])
def question_list(db: Session = Depends(get_db)):
    """
    저장된 모든 질문 목록을 조회하는 API입니다.
    """
    _question_list = question_crud.get_question_list(db)
    return _question_list


@router.post('/create', status_code=204)
def question_create(_question_create: question_schema.QuestionCreate,
                    db: Session = Depends(get_db)):
    """
    새로운 질문을 등록하는 API입니다.
    """
    question_crud.create_question(db=db, question_create=_question_create)