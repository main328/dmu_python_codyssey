# chat_client.py
# 채팅 서버에 접속하여 메시지를 주고받는 최종 클라이언트 프로그램

import socket
import threading

def receive_messages(client_socket):
    """
    서버로부터 메시지를 계속 수신하고 출력하는 함수 (쓰레드에서 실행)
    """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message or message == '[오류] 이미 사용 중인 닉네임입니다.':
                print(message)
                break
            print(message)
        except (ConnectionResetError, ConnectionAbortedError):
            print('[알림] 서버와의 연결이 끊어졌습니다.')
            break
        except Exception as e:
            print(f'[오류] 메시지 수신 중 오류 발생: {e}')
            break
    
    # 수신이 끝나면 소켓을 닫고 프로그램 종료 준비
    print('[알림] 수신 쓰레드를 종료합니다.')
    client_socket.close()

def start_client():
    """
    클라이언트를 시작하고 서버에 접속
    """
    host = '127.0.0.1'  # 서버와 동일한 호스트
    port = 9999         # 서버와 동일한 포트

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except socket.error as e:
        print('[오류] 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.')
        print(f'[상세 오류] {e}')
        return

    # 1. 닉네임 입력 및 전송
    while True:
        nickname = input('사용할 닉네임을 입력하세요: ')
        if nickname:
            client_socket.send(nickname.encode('utf-8'))
            break
        else:
            print('닉네임은 공백일 수 없습니다.')
    
    # 2. 메시지 수신을 위한 쓰레드 시작
    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receiver_thread.daemon = True # 메인 프로그램 종료 시 함께 종료
    receiver_thread.start()

    print(f"'{nickname}'님, 서버에 접속했습니다. '/종료'를 입력하면 나갑니다.")
    print("귓속말 사용법: /w 상대방닉네임 메시지")

    # 3. 사용자 입력 메시지 전송
    try:
        while receiver_thread.is_alive():
            message = input()
            if not client_socket._closed:
                client_socket.send(message.encode('utf-8'))
                if message == '/종료':
                    break
            else:
                break
    except KeyboardInterrupt:
        print('[알림] 프로그램을 종료합니다.')
    finally:
        if receiver_thread.is_alive():
            print("[알림] 연결을 종료합니다.")
        client_socket.close()

if __name__ == '__main__':
    start_client()

