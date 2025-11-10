# model.py
from pydantic import BaseModel

class TodoItem(BaseModel):
    """
    할 일 수정(PUT) 요청 시 사용될 Pydantic 모델입니다.
    클라이언트는 수정할 'task_name'만 본문(body)에 담아 전송합니다.
    id는 URL 경로를 통해 전달받으므로 이 모델에는 포함되지 않습니다.

    Attributes:
        task_name (str): 수정할 새로운 할 일의 이름.
    """
    task_name: str