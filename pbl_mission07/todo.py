import csv
import os
from fastapi import FastAPI, APIRouter, HTTPException

# --- 1. FastAPI 앱 및 전역 설정 ---
app = FastAPI()
router = APIRouter()

TODO_FILE = 'todo_list.csv'
TODO_FIELDS = ['task_name', 'description']

# '무상태(Stateless)' 설계를 위해 전역 todo_list 리스트를 사용하지 않습니다.


# --- 2. 헬퍼 함수 (CSV I/O) ---

def check_or_create_csv():
    '''
    서버 시작 시 파일이 없으면 헤더를 포함하여 생성합니다.
    '''
    if not os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(TODO_FIELDS)
            print(f"'{TODO_FILE}'이(가) 없어 새로 생성했습니다.")
        except IOError as e:
            # 시작 시 파일 생성 실패는 심각한 오류입니다.
            print(f"CRITICAL: CSV 파일 생성에 실패했습니다: {e}")
            # 서버 시작을 중단시키기 위해 예외를 다시 발생시킵니다.
            raise e


def get_all_todos_from_file() -> list:
    '''
    'GET /list' 요청 시 호출됩니다.
    항상 파일에서 직접 모든 데이터를 읽어 리스트로 반환합니다.
    '''
    try:
        with open(TODO_FILE, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except IOError as e:
        print(f"CSV 파일 읽기 실패 (GET /list): {e}")
        # 사용자에게 500 오류를 반환합니다.
        raise HTTPException(status_code=500, detail="데이터 파일에 접근할 수 없습니다.")
    except csv.Error as e:
        # csv.Error는 파일이 손상되었을 가능성을 의미합니다.
        print(f"CSV 파일 파싱 오류: {e}")
        raise HTTPException(status_code=500, detail="데이터 파일이 손상되었습니다.")

def append_todo_to_csv(item: dict) -> dict:
    '''
    'POST /add' 요청 시 호출됩니다.
    CSV 파일에 한 줄을 추가(append)합니다.
    '''
    # CSV 필드에 맞게 수동으로 딕셔너리 필터링
    filtered_item = {}
    for key in TODO_FIELDS:
        filtered_item[key] = item.get(key, '')

    try:
        with open(TODO_FILE, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=TODO_FIELDS)
            writer.writerow(filtered_item)
        
        return filtered_item  # 성공 시 추가된 항목 반환
    except IOError as e:
        print(f"CSV 파일 쓰기 실패 (POST /add): {e}")
        # 사용자에게 500 오류를 반환합니다.
        raise HTTPException(status_code=500, detail="데이터 파일에 쓸 수 없습니다.")


# --- 3. FastAPI 이벤트 핸들러 ---

@app.on_event('startup')
def on_startup():
    '''
    서버가 시작될 때 CSV 파일 존재 여부를 확인하고 생성합니다.
    (contextlib가 허용되지 않으므로 on_event를 사용합니다)
    '''
    print('서버가 시작됩니다. CSV 파일 상태를 확인합니다.')
    check_or_create_csv()


# --- 4. APIRouter 라우트 정의 ---

@router.post('/add')
def add_todo(item: dict):
    '''
    POST 방식 (/add):
    새로운 할 일을 받아 CSV 파일에 '추가'합니다.
    '''
    
    # --- Pydantic 대신 수동 검증 ---
    
    # 1. 보너스 과제 (빈 딕셔너리)
    if not item:
        raise HTTPException(status_code=400, detail="입력 데이터가 비어있습니다.")
    
    # 2. 핵심 데이터('task_name') 검증
    task_name = item.get('task_name')
    
    # 'task_name'이 없거나, 타입이 문자열이 아니거나, 앞뒤 공백 제거 시 빈 문자열인 경우
    if not task_name or not isinstance(task_name, str) or len(task_name.strip()) == 0:
        raise HTTPException(
            status_code=422,  # 422 (Unprocessable Entity)가 더 적합
            detail="필수 필드 'task_name'이 없거나 비어있습니다."
        )
    # --- 검증 끝 ---

    # 파일 쓰기 함수 호출 (실패 시 이 함수가 500 오류를 발생시킴)
    added_item = append_todo_to_csv(item)
    
    # 성공 응답 반환
    return {'status': 'success', 'added_item': added_item}


@router.get('/list')
def retrieve_todo(): # <- 반환 타입 힌트(-> list)를 제거했습니다.
    '''
    GET 방식 (/list):
    파일에서 모든 데이터를 읽어옵니다.
    데이터가 없으면 안내 문구를 반환합니다.
    '''
    # 1. 파일에서 모든 할 일 목록을 가져옵니다.
    todo_list = get_all_todos_from_file()
    
    # 2. 리스트가 비어있는지(데이터가 없는지) 확인합니다.
    if not todo_list:
        # 3. 리스트가 비어있다면, 200 OK 상태와 함께 안내 메시지(dict)를 반환합니다.
        return {"message": "현재 등록된 할 일이 없습니다."}
    
    # 4. 리스트에 데이터가 있다면, 기존처럼 리스트를 반환합니다.
    return todo_list


# --- 5. 라우터를 메인 앱에 포함 ---
app.include_router(router, prefix='/api')