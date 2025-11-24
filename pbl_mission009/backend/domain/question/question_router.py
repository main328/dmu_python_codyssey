from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.question import question_schema, question_crud

router = APIRouter(
    prefix='/api/question',
)


@router.get('/list', response_model=list[question_schema.Question])
def question_list(db: Session = Depends(get_db)):
    """
    저장된 모든 질문 목록을 조회하는 API입니다.

    Args:
        db (Session): 의존성 주입을 통해 받은 DB 세션

    Returns:
        list[Question]: 질문 데이터 리스트

    Raises:
        HTTPException(500): DB 조회 중 오류 발생 시
    """
    try:
        _question_list = question_crud.get_question_list(db)
        return _question_list
    except Exception as e:
        # 실제 운영 시에는 에러 로그(Log)를 남겨야 합니다.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post('/create', status_code=status.HTTP_204_NO_CONTENT)
def question_create(
    _question_create: question_schema.QuestionCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 질문을 등록하는 API입니다.

    Args:
        _question_create (QuestionCreate): 요청 본문(Body) 데이터
        db (Session): 의존성 주입을 통해 받은 DB 세션

    Returns:
        None: 성공 시 204 No Content 반환

    Raises:
        HTTPException(500): DB 저장 중 오류 발생 시
    """
    try:
        question_crud.create_question(db=db, question_create=_question_create)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 저장 중 오류가 발생했습니다: {str(e)}"
        )