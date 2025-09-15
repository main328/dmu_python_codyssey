# web_server_http_client.py
# 제출하신 코드를 기반으로 오류를 수정하고 개선한 최종 서버 프로그램

import http.server
import http.client
from datetime import datetime

# 서버의 기본 설정을 정의합니다.
PORT = 8080

# 요청을 처리하는 핸들러 클래스
class WebServer(http.server.BaseHTTPRequestHandler):
    """
    BaseHTTPRequestHandler를 상속받아 GET 요청을 처리하는 핸들러 클래스입니다.
    """
    def do_GET(self):
        """
        웹 브라우저로부터 GET 요청을 받았을 때 자동으로 호출됩니다.
        클라이언트 정보를 로그로 남기고, index.html 파일을 전송합니다.

        Args:
            None

        Returns:
            None
        """
        # --- 1. 접속자 정보 로그 기록 ---
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # ※ 변수 이름 오타 수정: client_adress -> client_address
        client_address = self.client_address[0]
        
        # --- 테스트를 위해 실제 IP 대신 공인 IP로 강제 설정 ---
        # 실제 운영 시에는 아래 라인을 주석 처리하거나 삭제해야 합니다.
        client_address = '223.38.86.119'
        
        accept_language = self.headers.get('Accept-Language', '정보 없음')

        print(f'--- 클라이언트 접속 정보 ---')
        print(f'접속 시간: {current_time}')
        print(f'IP 주소: {client_address}')
        print(f'선호 언어: {accept_language}')
        
        # 위치 정보 조회 함수 호출
        self.log_location_info(client_address)
        print(f'--------------------------\n')

        try:
            # --- 2. index.html 파일 읽기 ---
            with open('index.html', 'rb') as file:
                content = file.read()

            # --- 3. 성공 응답(200 OK) 전송 ---
            self.send_response(200)
            
            # --- 4. HTTP 헤더 전송 ---
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # --- 5. HTML 콘텐츠(본문) 전송 ---
            self.wfile.write(content)

        except FileNotFoundError:
            # index.html 파일을 찾을 수 없을 때 처리
            self.send_error(404, 'HTML 콘텐츠를 찾을 수 없습니다.')

    # ※ 인자 순서 및 이름을 더 명확하게 수정: (key, value) -> (response_text, key)
    def _parse_response(self, response_text, key):
        """
        (도우미 함수) JSON과 유사한 텍스트에서 특정 키(key)에 해당하는 값(value)을 수동으로 찾아냅니다.

        Args:
            response_text (str): 파싱할 전체 응답 텍스트입니다.
            key (str): 찾고자 하는 값의 키(key)입니다.

        Returns:
            str: 찾아낸 값(value) 문자열. 찾지 못하면 'N/A'를 반환합니다.
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
        """
        http.client를 사용하여 IP 주소를 기반으로 위치 정보를 조회하고 출력합니다.

        Args:
            ip_address (str): 조회할 클라이언트의 IP 주소입니다.

        Returns:
            None
        """
        if ip_address == '127.0.0.1':
            print('위치 정보: 로컬호스트 (조회 안 함)')
            return
            
        try:
            conn = http.client.HTTPConnection('ip-api.com')
            conn.request('GET', f'/json/{ip_address}')
            
            response = conn.getresponse()
            response_text = response.read().decode('utf-8')
            
            conn.close()
            
            # ※ 올바른 인자 순서로 함수 호출
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

        except Exception as error:
            print(f'[오류] 위치 정보 조회 중 오류가 발생했습니다: {error}')


def run_server():
    """
    HTTP 서버를 생성하고 Ctrl+C를 누를 때까지 무한히 실행합니다.
    """
    server_address = ('', PORT)
    # ※ 변수 이름 일관성: set_http -> httpd
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

