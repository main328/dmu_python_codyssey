# web_server_socket.py
# socket 모듈을 직접 사용하고, json 모듈 없이 응답을 수동으로 파싱하는 웹 서버입니다.

import http.server
import socket # http.client 대신 socket을 직접 임포트합니다.
# json 모듈을 더 이상 사용하지 않으므로 import 문을 제거합니다.

# 서버의 기본 설정을 정의합니다.
PORT = 8080

# 요청을 처리하는 핸들러 클래스
class WebServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """ GET 요청을 처리합니다. """
        current_time = self.date_time_string()
        # client_address = self.client_address[0]
        client_address = '223.38.86.119'
        accept_language = self.headers.get('Accept-Language', '정보 없음')

        print(f'--- 클라이언트 접속 정보 ---')
        print(f'접속 시간: {current_time}')
        print(f'IP 주소: {client_address}')
        print(f'선호 언어: {accept_language}')
        
        self.log_location_info(client_address)
        print(f'--------------------------\n')

        try:
            with open('index.html', 'rb') as file:
                content = file.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'HTML 콘텐츠를 찾을 수 없습니다.')

    def _parse_response(self, response_text, key):
        """
        (도우미 함수) JSON과 유사한 텍스트에서 특정 키(key)에 해당하는 값(value)을 수동으로 찾아냅니다.
        """
        search_pattern = f'"{key}":"'
        start_index = response_text.find(search_pattern)
        if start_index == -1:
            return 'N/A'
        
        value_start_index = start_index + len(search_pattern)
        end_index = response_text.find('"', value_start_index)
        if end_index == -1:
            return 'N/A'
            
        return response_text[value_start_index:end_index]

    def log_location_info(self, ip_address):
        """ (socket 직접 사용) IP 주소를 기반으로 위치 정보를 조회합니다. """
        if ip_address == '127.0.0.1':
            print('위치 정보: 로컬호스트 (조회 안 함)')
            return
            
        try:
            # 1. TCP 소켓을 생성하고 ip-api.com에 접속합니다.
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('ip-api.com', 80))

            # 2. HTTP GET 요청 헤더를 직접 만듭니다.
            request_header = (
                f'GET /json/{ip_address} HTTP/1.1\r\n'
                f'Host: ip-api.com\r\n'
                f'Connection: close\r\n\r\n'
            )
            
            # 3. 요청을 전송합니다.
            client_socket.sendall(request_header.encode('utf-8'))

            # 4. 응답을 모두 수신합니다.
            response_chunks = []
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_chunks.append(chunk)
            
            full_response = b''.join(response_chunks)
            client_socket.close()

            # 5. 응답에서 헤더와 본문을 분리합니다.
            header_part, body_part = full_response.split(b'\r\n\r\n', 1)
            
            # *** 여기가 핵심 변경점입니다! ***
            # 6. 본문을 문자열로 변환합니다.
            response_text = body_part.decode('utf-8')

            # 7. json.loads() 대신, 수동으로 만든 파싱 함수를 사용합니다.
            status = self._parse_response(response_text, 'status')

            if status == 'success':
                country = self._parse_response(response_text, 'country')
                city = self._parse_response(response_text, 'city')
                isp = self._parse_response(response_text, 'isp')
                print(f'위치 정보: {city}, {country}')
                print(f'ISP 정보: {isp}')
            else:
                message = self._parse_response(response_text, 'message')
                print(f'위치 정보: 조회 실패 ({message})')

        except Exception as e:
            print(f'[오류] 위치 정보 조회 중 오류 발생: {e}')


def run_server():
    """ HTTP 서버를 생성하고 실행합니다. """
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, WebServer)
    
    print(f'[알림] 서버가 {PORT} 포트에서 실행되었습니다.')
    print(f'웹 브라우저에서 http://localhost:{PORT} 로 접속하세요.')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n[알림] 사용자의 요청으로 서버를 종료합니다.')
    finally:
        httpd.server_close()
        print('[알림] 서버가 성공적으로 종료되었습니다.')

if __name__ == '__main__':
    run_server()

