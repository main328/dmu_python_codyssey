# chat_server_oop_final.py
# 제출하신 코드를 기반으로 오류를 수정하고 개선한 최종 서버 프로그램

import socket
import threading

# 각 클라이언트 연결을 처리하는 클래스 (threading.Thread 상속)
class ClientHandler(threading.Thread):
    # --- 초기화 메서드 ---
    # ClientHandler 객체가 생성될 때 호출됩니다.
    def __init__(self, server, client_socket, address):
        '''
        Args:
            server (ChatServer): 이 핸들러를 생성한 메인 ChatServer 객체.
            client_socket (socket.socket): 클라이언트와 연결된 전용 소켓.
            address (tuple): 클라이언트의 주소 정보 (IP, 포트).
        '''
        # 부모 클래스인 threading.Thread의 초기화 기능을 반드시 호출해야 합니다.
        super().__init__()
        
        self.server = server
        self.client_socket = client_socket
        self.address = address
        self.nickname = ''
    
    # --- 쓰레드 메인 로직 ---
    # .start() 메서드가 호출되면 이 run() 메서드가 새로운 쓰레드에서 실행됩니다.
    def run(self):
        ''' 쓰레드의 메인 로직. 닉네임 설정, 메시지 수신 및 처리를 담당합니다. '''
        try:
            # 1. 닉네임 설정 단계
            while True:
                # 클라이언트로부터 닉네임 후보를 수신합니다. (최대 1024바이트)
                nickname_candidate = self.client_socket.recv(1024).decode('utf-8')

                # 클라이언트가 닉네임 입력 전 연결을 종료한 경우, 쓰레드를 종료합니다.
                if not nickname_candidate:
                    return

                # 서버에 닉네임 중복 여부를 확인합니다.
                if self.server.is_nickname_duplicate(nickname_candidate):
                    # 중복 시, 클라이언트에게 'DUPLICATE_NICKNAME' 신호를 보냅니다.
                    self.client_socket.send('DUPLICATE_NICKNAME'.encode('utf-8'))
                else:
                    # 사용 가능 시, 닉네임을 확정하고 'NICKNAME_OK' 신호를 보낸 후 루프를 탈출합니다.
                    self.nickname = nickname_candidate
                    self.client_socket.send('NICKNAME_OK'.encode('utf-8'))
                    break
            
            # 2. 클라이언트 등록 및 입장 알림
            # 서버의 전체 클라이언트 목록에 자신을 추가합니다.
            self.server.add_client(self, self.nickname)
            print(f'[알림] {self.nickname}님이 연결되었습니다: {self.address}')

            # 모든 접속자에게 새로운 사용자의 입장을 알립니다. (자신은 제외)
            self.server.broadcast(f'{self.nickname}님이 입장하셨습니다.', self)

        except Exception as error:
            print(f'[오류] 클라이언트 처리 중 오류가 발생했습니다: {error}')
            # 닉네임 설정 실패 시에도 연결을 안전하게 닫도록 finally로 이동
            return
        finally:
            # 닉네임이 설정되지 않은 상태로 이 블록에 도달했다면(오류 등), 소켓을 닫습니다.
            if not self.nickname:
                self.client_socket.close()
        
        # 3. 메시지 수신 및 처리 루프
        while True:
            try:
                # 클라이언트로부터 메시지를 수신합니다.
                message = self.client_socket.recv(1024).decode('utf-8')

                # 메시지가 없거나(정상 종료) '/종료' 명령어일 경우 루프를 탈출합니다.
                if not message or message == '/종료':
                    break
                
                # 귓속말 명령어 처리
                if message.startswith('/w '):
                    self.server.handle_whisper(self, message)
                # 일반 메시지 처리
                else:
                    print(f'[메시지] {self.nickname}> {message}')
                    self.server.broadcast(f'{self.nickname}> {message}', self)
            
            except ConnectionResetError:
                # 클라이언트가 비정상적으로 연결을 끊었을 때 처리
                break
            except Exception as error:
                print(f'[오류] 메시지 수신 중 오류가 발생했습니다 ({self.nickname}): {error}')
                break
        
        # 4. 연결 종료 처리
        # 루프가 종료되면 클라이언트를 목록에서 제거하고 퇴장 메시지를 보냅니다.
        self.server.remove_client(self)

# 서버의 전체적인 운영을 관리하는 메인 클래스
class ChatServer:
    # --- 초기화 메서드 ---
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {ClientHandler 객체: 닉네임}
        self.client_lock = threading.Lock()

    # --- 서버 시작 메서드 ---
    def start(self):
        ''' 서버 소켓을 생성하고 클라이언트의 접속을 무한 대기합니다. '''
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f'[알림] 채팅 서버를 실행합니다. ({self.host}:{self.port})')

            while True:
                # 클라이언트의 연결 요청을 수락합니다. (블로킹)
                client_socket, address = self.server_socket.accept()
                # 각 클라이언트를 전담할 쓰레드를 생성하고 시작합니다.
                client_handler = ClientHandler(self, client_socket, address)
                client_handler.start()
        except KeyboardInterrupt:
            print('[알림] 채팅 서버를 종료합니다.')
        except Exception as error:
            print(f'[오류] 서버 실행 중 오류가 발생했습니다: {error}')
        finally:
            if self.server_socket:
                self.server_socket.close() # ※ .close() 괄호를 추가하여 함수를 올바르게 호출

    # --- 메시지 브로드캐스트 메서드 ---
    def broadcast(self, message, sender=None):
        ''' 모든 클라이언트에게 메시지를 전송합니다. (메시지를 보낸 사람은 제외) '''
        # ※ 교착 상태(deadlock) 방지를 위해 구조 변경
        # 전송에 실패한 클라이언트를 임시로 저장할 리스트
        failed_clients = []
        with self.client_lock:
            # 반복 중 딕셔너리 변경 오류를 방지하기 위해 리스트로 복사하여 순회합니다.
            for client in list(self.clients):
                # 메시지를 보낸 사람(sender)을 제외한 모든 사람에게 메시지를 보냅니다.
                if client != sender:
                    try:
                        client.client_socket.send(message.encode('utf-8'))
                    except Exception as error:
                        print(f'[오류] {self.clients.get(client)}에게 메시지 전송 중 오류: {error}')
                        # lock이 걸린 상태에서 remove_client를 바로 호출하면 교착 상태가 발생할 수 있으므로,
                        # 실패한 클라이언트를 리스트에 추가만 해둡니다.
                        failed_clients.append(client)

        # lock이 해제된 후에, 실패한 클라이언트들의 연결을 종료합니다.
        for client in failed_clients:
            self.remove_client(client)

    # --- 귓속말 처리 메서드 ---
    def handle_whisper(self, sender, message):
        ''' 귓속말 명령어를 해석하고, 대상 클라이언트에게 메시지를 전송합니다. '''
        # ※ 귓속말 형식 검증 로직 수정
        parts = message.split(' ', 2)
        if len(parts) < 3:
            sender.client_socket.send('[알림] 귓속말 형식이 올바르지 않습니다. (사용법: /w 닉네임 메시지)'.encode('utf-8'))
            return

        target_nickname, whisper_msg = parts[1], parts[2]
        target_client = None

        with self.client_lock:
            for client, nickname in self.clients.items():
                if nickname == target_nickname:
                    target_client = client
                    break
        
        if target_client:
            # 귓속말을 받는 사람에게 메시지 전송
            target_client.client_socket.send(f'[귓속말 from {sender.nickname}] {whisper_msg}'.encode('utf-8'))
            # 귓속말을 보낸 사람에게도 확인 메시지 전송
            sender.client_socket.send(f'[{target_nickname}님에게 귓속말] {whisper_msg}'.encode('utf-8'))
        else:
            sender.client_socket.send(f'[알림] {target_nickname}님을 찾을 수 없습니다.'.encode('utf-8'))

    # --- 클라이언트 관리 메서드 ---
    def add_client(self, client, nickname):
        ''' 새로운 클라이언트를 목록에 추가합니다. '''
        with self.client_lock:
            self.clients[client] = nickname

    def remove_client(self, client):
        ''' 클라이언트 목록에서 특정 클라이언트를 제거하고 퇴장 메시지를 전송합니다. '''
        # ※ 교착 상태(deadlock) 방지를 위해 구조 변경
        nickname = None
        # 먼저 lock을 걸고 안전하게 클라이언트 목록에서 해당 클라이언트를 제거합니다.
        with self.client_lock:
            if client in self.clients:
                nickname = self.clients.pop(client)
                print(f'[알림] {nickname}님이 접속을 종료했습니다.')
        
        # lock이 해제된 후에 퇴장 메시지를 브로드캐스트합니다.
        # 이렇게 하면 remove_client가 broadcast를, broadcast가 다시 remove_client를 호출하더라도
        # lock을 중복으로 점유하지 않아 교착 상태가 발생하지 않습니다.
        if nickname:
            self.broadcast(f'{nickname}님이 퇴장하셨습니다.')
        
        # 모든 처리가 끝난 후 소켓을 닫습니다.
        client.client_socket.close()

    def is_nickname_duplicate(self, nickname):
        ''' 닉네임 중복 여부를 확인합니다. '''
        with self.client_lock:
            return nickname in self.clients.values()

# --- 프로그램 시작점 ---
if __name__ == '__main__':
    # ※ 서버 객체 생성 시 host와 port를 인자로 전달하도록 수정
    server = ChatServer('127.0.0.1', 9999)
    server.start()

