# main.py
import csv
import os
from fastapi import FastAPI, APIRouter, HTTPException
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Union

# --- 1. 모델 임포트 및 전역 설정 ---
from model import TodoItem

# 전역 상수 정의
TODO_FILE = 'todo_list.csv'
TODO_FIELDS = ['id', 'task_name']

# --- 2. FastAPI 앱 및 Lifespan 관리자 ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 앱의 생명주기(Lifespan) 이벤트 핸들러입니다.
    서버 시작 시 CSV 파일의 존재 여부를 확인하고, 없으면 생성합니다.
    
    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스.
    
    Yields:
        None: FastAPI 앱이 실행되는 동안 제어권을 넘깁니다.
    """
    print('서버가 시작됩니다. CSV 파일 상태를 확인합니다.')
    check_or_create_csv()
    yield
    print('서버가 종료됩니다.')

app = FastAPI(lifespan=lifespan)
router = APIRouter()


# --- 3. 헬퍼 함수 (CSV I/O) ---

def check_or_create_csv():
    """
    서버 시작 시 `TODO_FILE`의 존재 여부를 확인합니다.
    파일이 존재하지 않으면, `TODO_FIELDS`를 헤더로 하는 새 CSV 파일을 생성합니다.
    
    Raises:
        IOError: 파일 시스템 권한 등의 문제로 파일 생성에 실패할 경우,
                 서버 시작을 중단시키기 위해 예외를 다시 발생시킵니다.
    """
    if not os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(TODO_FIELDS)
            print(f"'{TODO_FILE}'이(가) 없어 새로 생성했습니다.")
        except IOError as e:
            print(f"CRITICAL: CSV 파일 생성에 실패했습니다: {e}")
            raise e


def get_all_todos_from_file() -> List[Dict[str, Any]]:
    """
    `TODO_FILE`에서 모든 할 일 목록을 읽어 리스트로 반환합니다.
    CSV에서 읽은 'id' 값을 문자열(str)에서 숫자(int)로 변환합니다.

    Returns:
        List[Dict[str, Any]]: 
            모든 할 일 항목의 딕셔너리 리스트.
            (예: [{'id': 1, 'task_name': 'Buy milk'}, ...])
            'id'는 정수(int) 타입으로 변환됩니다.

    Raises:
        HTTPException (500): 
            - IOError: 파일 읽기 권한이 없거나 파일을 찾을 수 없는 경우.
            - csv.Error: CSV 파일 형식이 손상되어 파싱에 실패한 경우.
    """
    try:
        with open(TODO_FILE, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            todos = []
            for row in reader:
                try:
                    # 'id'를 숫자로 변환 (max() 계산 및 경로 매개변수 비교를 위함)
                    row['id'] = int(row['id'])
                    todos.append(row)
                except (ValueError, KeyError, TypeError):
                    print(f"손상된 행을 건너뜁니다: {row}")
            return todos
    except IOError as e:
        print(f"CSV 파일 읽기 실패: {e}")
        raise HTTPException(status_code=500, detail='데이터 파일에 접근할 수 없습니다.')
    except csv.Error as e:
        print(f"CSV 파일 파싱 오류: {e}")
        raise HTTPException(status_code=500, detail='데이터 파일이 손상되었습니다.')


def write_all_todos_to_file(todo_list: List[Dict[str, Any]]):
    """
    메모리 상의 'todo_list' 전체를 `TODO_FILE`에 덮어씁니다(Overwrite).
    주로 PUT(수정) 또는 DELETE(삭제) 작업 후에 호출됩니다.

    Args:
        todo_list (List[Dict[str, Any]]): 
            파일에 새로 덮어쓸 전체 할 일 목록. 
            딕셔너리의 키는 `TODO_FIELDS`와 일치해야 합니다.

    Raises:
        HTTPException (500): 
            - IOError: 파일 쓰기 권한이 없는 경우.
    """
    try:
        with open(TODO_FILE, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=TODO_FIELDS)
            writer.writeheader()
            writer.writerows(todo_list)
    except IOError as e:
        print(f"CSV 파일 쓰기 실패 (Update/Delete): {e}")
        raise HTTPException(status_code=500, detail='데이터 파일에 쓸 수 없습니다.')


def append_todo_to_csv(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    새로운 할 일 항목(item) 하나를 `TODO_FILE`의 맨 끝에 추가(Append)합니다.
    POST /add 요청 시에만 사용됩니다.

    Args:
        item (Dict[str, Any]): 
            CSV에 추가할 단일 할 일 항목. 
            `TODO_FIELDS` (id, task_name) 키를 포함해야 합니다.

    Returns:
        Dict[str, Any]: 성공적으로 파일에 추가된 'item' 딕셔너리.

    Raises:
        HTTPException (500): 
            - IOError: 파일 쓰기(append) 권한이 없는 경우.
    """
    # 필터링: item에 불필요한 키가 있어도 TODO_FIELDS만 골라서 저장
    filtered_item = {}
    for key in TODO_FIELDS:
        filtered_item[key] = item.get(key, '')

    try:
        with open(TODO_FILE, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=TODO_FIELDS)
            writer.writerow(filtered_item)
        
        return filtered_item
    except IOError as e:
        print(f"CSV 파일 쓰기 실패 (POST /add): {e}")
        raise HTTPException(status_code=500, detail='데이터 파일에 쓸 수 없습니다.')


# --- 4. APIRouter 라우트 정의 ---

@router.post('/add', status_code=201) # 201 Created가 더 적합
def add_todo(item: Dict[str, Any]):
    """
    POST /api/add
    새로운 할 일을 생성합니다. 'id'는 자동으로 1씩 증가하여 할당됩니다.
    
    Args:
        item (Dict[str, Any]):
            HTTP 요청의 본문(body). Pydantic을 사용하지 않고 수동 검증.
            (예: {"task_name": "New Task"})
            
    Returns:
        Dict[str, Any]: 
            성공 상태 및 추가된 항목 (새 'id' 포함).
            (예: {"status": "success", "added_item": {"id": 1, "task_name": "New Task"}})

    Raises:
        HTTPException (400): 요청 본문(body)이 비어있는 경우 (예: {}).
        HTTPException (422): 'task_name'이 없거나 비어있는 경우.
        HTTPException (409): 'task_name'이 이미 존재하는 경우 (중복 방지).
        HTTPException (500): CSV 파일 I/O 실패 시.
    """
    # 1. 수동 유효성 검사
    if not item:
        raise HTTPException(status_code=400, detail='입력 데이터가 비어있습니다.')
    
    task_name = item.get('task_name')
    
    if not task_name or not isinstance(task_name, str) or len(task_name.strip()) == 0:
        raise HTTPException(
            status_code=422,
            detail="필수 필드 'task_name'이 없거나 비어있습니다."
        )
    
    task_name = task_name.strip()

    # 2. ID 계산 및 중복 검사를 위해 모든 데이터 읽기
    todo_list = get_all_todos_from_file()
    
    # 3. task_name 중복 검사
    for todo in todo_list:
        if todo['task_name'] == task_name:
            raise HTTPException(status_code=409, detail=f"'{task_name}' 작업이 이미 존재합니다.")

    # 4. 새 ID 계산 (데이터가 없으면 1, 있으면 max + 1)
    next_id = 1
    if todo_list:
        max_id = max(todo.get('id', 0) for todo in todo_list)
        next_id = max_id + 1
    
    new_item_data = {
        'id': next_id,
        'task_name': task_name
    }

    # 5. 파일에 추가 (I/O 오류는 이 함수가 처리)
    added_item = append_todo_to_csv(new_item_data)
    
    return {'status': 'success', 'added_item': added_item}


@router.get('/list')
def retrieve_todo() -> Union[List[Dict[str, Any]], Dict[str, str]]:
    """
    GET /api/list
    저장된 모든 할 일 목록을 반환합니다.
    
    Returns:
        Union[List[Dict[str, Any]], Dict[str, str]]:
            - 할 일이 있는 경우: 전체 할 일 딕셔너리 리스트.
            - 할 일이 없는 경우: 안내 메시지 딕셔너리.
    
    Raises:
        HTTPException (500): CSV 파일 읽기 실패 시.
    """
    todo_list = get_all_todos_from_file()
    
    if not todo_list:
        return {'message': '현재 등록된 할 일이 없습니다.'}
    
    return todo_list


# --- 5. ID 기반 개별 조회, 수정, 삭제 ---

@router.get('/todo/{todo_id}')
def get_single_todo(todo_id: int) -> Dict[str, Any]:
    """
    GET /api/todo/{todo_id}
    특정 'id'를 가진 할 일 항목 1개를 조회합니다.
    
    Args:
        todo_id (int): 
            URL 경로 매개변수로부터 전달받는 조회할 항목의 고유 'id'.
            
    Returns:
        Dict[str, Any]: 'id'와 일치하는 할 일 딕셔너리.

    Raises:
        HTTPException (404): 해당 'id'를 가진 항목이 없는 경우.
        HTTPException (500): CSV 파일 읽기 실패 시.
    """
    todo_list = get_all_todos_from_file()
    
    for todo in todo_list:
        if todo['id'] == todo_id:
            return todo
    
    raise HTTPException(status_code=404, detail=f'ID {todo_id}의 할 일을 찾을 수 없습니다.')


@router.put('/todo/{todo_id}')
def update_todo(todo_id: int, item: TodoItem) -> Dict[str, Any]:
    """
    PUT /api/todo/{todo_id}
    특정 'id'를 가진 할 일의 'task_name'을 수정합니다.
    CSV 파일 전체를 덮어쓰는 방식으로 작동합니다.
    
    Args:
        todo_id (int): URL 경로 매개변수로부터 전달받는 수정할 항목의 'id'.
        item (TodoItem): 
            HTTP 요청 본문(body)으로부터 전달받는 Pydantic 모델.
            (예: {"task_name": "Updated Task"})
            
    Returns:
        Dict[str, Any]: 성공 상태 및 수정된 항목 (id, task_name).

    Raises:
        HTTPException (404): 해당 'id'를 가진 항목이 없는 경우.
        HTTPException (409): 수정하려는 'task_name'이 이미 다른 항목에 존재하는 경우.
        HTTPException (500): CSV 파일 I/O 실패 시.
    """
    todo_list = get_all_todos_from_file()
    
    updated_list = []
    found = False
    
    # 1. 메모리 상에서 리스트 수정
    for todo in todo_list:
        if todo['id'] == todo_id:
            updated_item_data = {
                'id': todo_id,
                'task_name': item.task_name
            }
            updated_list.append(updated_item_data)
            found = True
        else:
            updated_list.append(todo)
            
    if not found:
        raise HTTPException(status_code=404, detail=f'ID {todo_id}의 할 일을 찾을 수 없습니다.')

    # 2. 수정 시 중복 검사 (자신을 제외한 리스트 기준)
    existing_names = [t['task_name'] for t in updated_list if t['id'] != todo_id]
    if item.task_name in existing_names:
        raise HTTPException(status_code=409, detail=f"'{item.task_name}' 작업이 이미 존재합니다.")

    # 3. 파일 전체 덮어쓰기
    write_all_todos_to_file(updated_list)
    
    return {'status': 'success', 'updated_item': {'id': todo_id, 'task_name': item.task_name}}


@router.delete('/todo/{todo_id}')
def delete_single_todo(todo_id: int) -> Dict[str, str]:
    """
    DELETE /api/todo/{todo_id}
    특정 'id'를 가진 할 일 항목을 삭제합니다.
    CSV 파일 전체를 덮어쓰는 방식으로 작동합니다.
    
    Args:
        todo_id (int): URL 경로 매개변수로부터 전달받는 삭제할 항목의 'id'.
            
    Returns:
        Dict[str, str]: 성공 상태 및 안내 메시지.

    Raises:
        HTTPException (404): 해당 'id'를 가진 항목이 없는 경우.
        HTTPException (500): CSV 파일 I/O 실패 시.
    """
    todo_list = get_all_todos_from_file()
    
    # 1. 메모리 상에서 해당 id를 제외한 새 리스트 생성
    new_todo_list = [todo for todo in todo_list if todo['id'] != todo_id]
    
    if len(todo_list) == len(new_todo_list):
        # 리스트 길이에 변화가 없다면, 해당 id가 존재하지 않았음
        raise HTTPException(status_code=404, detail=f'ID {todo_id}의 할 일을 찾을 수 없습니다.')

    # 2. 파일 전체 덮어쓰기
    write_all_todos_to_file(new_todo_list)
    
    return {'status': 'success', 'message': f'ID {todo_id} 할 일이 삭제되었습니다.'}


# --- 6. 라우터를 메인 앱에 포함 ---
app.include_router(router, prefix='/api')
