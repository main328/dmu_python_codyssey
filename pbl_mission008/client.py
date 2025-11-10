# python client.py list
# python client.py add "새로운 할 일 1"
# python client.py get 1
# python client.py update 1 "수정된 할 일"
# python client.py delete 1


import requests
import argparse
import json
from typing import List, Union # <-- Union을 추가합니다.

# API 서버의 기본 주소입니다.
BASE_URL = 'http://127.0.0.1:8000/api'


def pretty_print(data: Union[dict, List[dict]]):
    """
    JSON 응답을 사람이 읽기 편하게 예쁘게 출력합니다.
    """
    print(json.dumps(data, indent=2, ensure_ascii=False))


def handle_error(response: requests.Response):
    """
    HTTP 오류 응답을 처리하고 사용자에게 메시지를 출력합니다.
    """
    try:
        # FastAPI (HTTPException)에서 보낸 오류 메시지를 출력
        detail = response.json()
        print(f"❌ 오류 발생 (HTTP {response.status_code}): {detail.get('detail', '알 수 없는 오류')}")
    except json.JSONDecodeError:
        # 서버가 JSON이 아닌 다른 응답(예: 500 HTML 오류)을 보낸 경우
        print(f"❌ 심각한 오류 (HTTP {response.status_code}): 서버 응답을 읽을 수 없습니다.")


def list_todos():
    """
    GET /api/list
    모든 할 일 목록을 가져와 출력합니다.
    """
    print("📋 모든 할 일 목록을 요청합니다...")
    try:
        response = requests.get(f'{BASE_URL}/list')
        
        if response.status_code == 200:
            pretty_print(response.json())
        else:
            handle_error(response)
            
    except requests.ConnectionError:
        print("❌ 연결 오류: API 서버가 실행 중인지 확인하세요.")


def add_todo(task_name: str):
    """
    POST /api/add
    새로운 할 일을 추가합니다.
    """
    print(f"✅ '{task_name}' 할 일을 추가합니다...")
    # Pydantic 모델을 사용하지 않으므로, dict를 직접 전송합니다.
    data = {'task_name': task_name}
    
    try:
        response = requests.post(f'{BASE_URL}/add', json=data)
        
        if response.status_code == 201: # 201 Created
            pretty_print(response.json())
        else:
            handle_error(response)

    except requests.ConnectionError:
        print("❌ 연결 오류: API 서버가 실행 중인지 확인하세요.")


def get_single_todo(todo_id: int):
    """
    GET /api/todo/{todo_id}
    특정 ID의 할 일을 조회합니다.
    """
    print(f"🔍 ID {todo_id} 할 일을 조회합니다...")
    try:
        response = requests.get(f'{BASE_URL}/todo/{todo_id}')
        
        if response.status_code == 200:
            pretty_print(response.json())
        else:
            handle_error(response)
            
    except requests.ConnectionError:
        print("❌ 연결 오류: API 서버가 실행 중인지 확인하세요.")


def update_todo(todo_id: int, new_task_name: str):
    """
    PUT /api/todo/{todo_id}
    특정 ID의 할 일을 수정합니다.
    """
    print(f"🔄 ID {todo_id} 할 일을 '{new_task_name}'(으)로 수정합니다...")
    # model.TodoItem (Pydantic 모델)에 맞는 JSON 데이터를 전송
    data = {'task_name': new_task_name}

    try:
        response = requests.put(f'{BASE_URL}/todo/{todo_id}', json=data)
        
        if response.status_code == 200:
            pretty_print(response.json())
        else:
            handle_error(response)
            
    except requests.ConnectionError:
        print("❌ 연결 오류: API 서버가 실행 중인지 확인하세요.")


def delete_todo(todo_id: int):
    """
    DELETE /api/todo/{todo_id}
    특정 ID의 할 일을 삭제합니다.
    """
    print(f"🗑️ ID {todo_id} 할 일을 삭제합니다...")
    try:
        response = requests.delete(f'{BASE_URL}/todo/{todo_id}')
        
        if response.status_code == 200:
            pretty_print(response.json())
        else:
            handle_error(response)
            
    except requests.ConnectionError:
        print("❌ 연결 오류: API 서버가 실행 중인지 확인하세요.")


def main():
    """
    argparse를 사용하여 커맨드 라인 입력을 처리하는 메인 함수
    """
    # 1. 메인 파서 생성
    parser = argparse.ArgumentParser(description="FastAPI To-Do 리스트 클라이언트")
    
    # 2. 하위 명령어(subparsers) 설정
    subparsers = parser.add_subparsers(dest='command', required=True, help='실행할 명령어')

    # 3. 'list' 명령어
    subparsers.add_parser('list', help='모든 할 일 목록을 조회합니다.')

    # 4. 'add' 명령어
    add_parser = subparsers.add_parser('add', help='새로운 할 일을 추가합니다.')
    add_parser.add_argument('task', type=str, help='추가할 할 일의 이름 (공백이 있으면 따옴표로 감싸세요)')

    # 5. 'get' 명령어
    get_parser = subparsers.add_parser('get', help='특정 ID의 할 일을 조회합니다.')
    get_parser.add_argument('id', type=int, help='조회할 할 일의 ID')

    # 6. 'update' 명령어
    update_parser = subparsers.add_parser('update', help='특정 ID의 할 일을 수정합니다.')
    update_parser.add_argument('id', type=int, help='수정할 할 일의 ID')
    update_parser.add_argument('task', type=str, help='새로운 할 일의 이름 (공백이 있으면 따옴표로 감싸세요)')

    # 7. 'delete' 명령어
    delete_parser = subparsers.add_parser('delete', help='특정 ID의 할 일을 삭제합니다.')
    delete_parser.add_argument('id', type=int, help='삭제할 할 일의 ID')

    # 8. 입력된 명령어 분석
    args = parser.parse_args()

    # 9. 명령어에 따라 적절한 함수 호출
    if args.command == 'list':
        list_todos()
    elif args.command == 'add':
        add_todo(args.task)
    elif args.command == 'get':
        get_single_todo(args.id)
    elif args.command == 'update':
        update_todo(args.id, args.task)
    elif args.command == 'delete':
        delete_todo(args.id)


if __name__ == "__main__":
    main()