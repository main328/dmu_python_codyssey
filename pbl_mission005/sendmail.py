# -*- coding: utf-8 -*-
"""
파일 목적: yagmail 라이브러리를 사용하여 Gmail 이메일을 간편하게 발송하는 스크립트입니다.
           메일 서버 관련 기능을 MailServer 클래스로 캡슐화하여 관리합니다.

주요 기능:
1. 스크립트 실행 시 사용자로부터 직접 입력받은 Gmail 계정과 앱 비밀번호를 이용해 SMTP 서버에 접속합니다.
2. 지정된 수신자에게 텍스트 이메일과 첨부 파일을 손쉽게 보냅니다.

사용 전 필수사항:
- `pip install yagmail` 명령어로 yagmail 라이브러리를 설치해야 합니다.
- 발신자로 사용할 Gmail 계정의 '2단계 인증'이 활성화되어 있어야 합니다.
- Google 계정 설정에서 '앱 비밀번호' (16자리)를 생성해야 합니다. 
"""

# --- 모듈 임포트 ---
# yagmail: SMTP 관련 복잡한 설정을 자동화하여 Gmail 발송을 매우 쉽게 만들어주는 라이브러리입니다.
import yagmail
# os: 파일 경로를 다루고 존재 여부를 확인하기 위해 사용합니다. (첨부 파일 처리용)
import os

class MailServer:
    """
    yagmail을 사용하여 Gmail SMTP 서버와의 연결 및 메일 발송을 관리하는 클래스입니다.
    """
    def __init__(self, sender_addr, app_password):
        """
        MailServer 인스턴스를 초기화하고 Gmail SMTP 서버에 로그인합니다.
        객체가 생성되는 시점에 서버에 연결하고 인증을 시도합니다.

        Args:
            sender_addr (str): 보내는 사람의 Gmail 주소.
            app_password (str): 보내는 사람 Gmail 계정의 16자리 앱 비밀번호.
        """
        # --- 목적: 발신자 이메일 주소 저장 ---
        self.sender_addr = sender_addr
        
        try:
            # --- yagmail 사용 양식 (서버 연결 및 로그인) ---
            # yagmail.SMTP()를 호출하면 다음 작업이 자동으로 수행됩니다:
            # 1. Gmail SMTP 서버('smtp.gmail.com')에 보안 연결(SSL/TLS)을 설정합니다.
            # 2. 제공된 계정과 앱 비밀번호로 로그인(인증)을 수행합니다.
            # 이 객체를 self.yag에 저장하여 클래스 내 다른 메서드에서 재사용합니다.
            self.yag = yagmail.SMTP(user=sender_addr, password=app_password)
            print(f"[INFO] '{sender_addr}' 계정으로 SMTP 서버에 성공적으로 연결되었습니다.")
        except Exception as e:
            # --- 목적: 연결 실패 시 예외 처리 ---
            print(f"[오류] SMTP 서버 연결 또는 로그인에 실패했습니다: {e}")
            print("- Gmail 주소와 16자리 앱 비밀번호가 정확한지 확인해주세요.")
            self.yag = None # 연결 실패 시 yag 객체를 None으로 설정하여 이후 작업 방지

    def send_email(self, receiver_addr, subject, body, attachment=None):
        """
        초기화된 SMTP 연결을 사용하여 이메일을 발송합니다.

        Args:
            receiver_addr (str): 받는 사람의 이메일 주소.
            subject (str): 이메일의 제목.
            body (str or list): 이메일의 본문 내용. 문자열 또는 리스트 형태가 가능합니다.
            attachment (str, optional): 첨부할 파일의 경로. 기본값은 None입니다.

        Returns:
            bool: 메일 발송 성공 시 True, 실패 시 False를 반환합니다.
        """
        # --- 목적: 서버 연결 상태 확인 ---
        # __init__ 단계에서 서버 연결에 실패했다면(self.yag가 None), 메일 발송을 시도하지 않고 함수를 종료합니다.
        if not self.yag:
            print("[오류] SMTP 서버가 연결되어 있지 않아 메일을 보낼 수 없습니다.")
            return False
            
        try:
            # --- yagmail 사용 양식 (이메일 발송) ---
            # yagmail의 send 메서드는 필수 및 선택적 인자를 받아 모든 과정을 자동으로 처리합니다.
            # to: 받는 사람의 이메일 주소. 리스트 형태로 여러 명에게 동시 발송 가능. (예: ['a@a.com', 'b@b.com'])
            # subject: 이메일 제목 (문자열).
            # contents: 이메일 본문. 일반 텍스트(str), HTML(str), 또는 여러 요소를 담은 리스트(list)도 가능.
            # attachments: 첨부 파일 경로. 단일 파일은 문자열로, 여러 파일은 리스트로 전달.
            self.yag.send(
                to=receiver_addr,
                subject=subject,
                contents=body,
                attachments=attachment
            )
            print(f"[성공] '{receiver_addr}' 주소로 메일을 성공적으로 발송했습니다.")
            return True
        except Exception as e:
            # --- 목적: 발송 중 발생할 수 있는 오류 처리 ---
            print(f"[오류] 메일 발송 중 문제가 발생했습니다: {e}")
            return False

# --- 목적: 스크립트의 메인 실행 블록 정의 ---
# 이 스크립트 파일이 직접 실행될 때만 아래 코드가 동작합니다.
# 다른 파일에서 이 파일을 'import'하여 사용할 경우에는 이 블록이 실행되지 않습니다.
if __name__ == "__main__":
    # --- 1. 사용자로부터 이메일 발송에 필요한 모든 정보 입력받기 ---
    print("--- 이메일 발송 정보 입력 ---")
    sender_email = input("보내는 사람의 Gmail 주소를 입력하세요: ")
    receiver_email = input("받는 사람의 이메일 주소를 입력하세요: ")
    
    print("\n[중요] Google 계정의 2단계 인증 후 생성된 '앱 비밀번호' 16자리를 입력해야 합니다.")
    app_pw = input("Gmail 앱 비밀번호를 입력하세요: ")

    print("\n--- 메일 내용 입력 ---")
    mail_subject = input("메일 제목: ")
    
    # --- 목적: 여러 줄의 본문 내용을 입력받기 위한 처리 ---
    print("메일 본문 (입력을 마치려면 새 줄에서 Ctrl+Z (Windows) 또는 Ctrl+D (macOS/Linux) 후 Enter):")
    body_lines = []
    try:
        # 사용자가 EOF(End-of-File) 신호를 보낼 때까지 여러 줄을 입력받습니다.
        while True:
            line = input()
            body_lines.append(line)
    except EOFError:
        pass # 사용자가 입력 종료 신호를 보내면 루프를 자연스럽게 빠져나옵니다.
    mail_body = "\n".join(body_lines) # 입력받은 여러 줄을 하나의 문자열로 합칩니다.
    
    # --- 2. 첨부 파일 처리 (선택 사항) ---
    attachment_path = None
    add_attachment = input("\n첨부 파일을 추가하시겠습니까? (y/n): ").lower()
    if add_attachment == 'y':
        attachment_path = 'report.txt' # 첨부할 파일 이름 지정
        # --- 목적: 첨부 파일이 없을 경우, 예제 파일을 동적으로 생성 ---
        if not os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'w', encoding='utf-8') as f:
                    f.write("이것은 yagmail로 자동 생성된 테스트 첨부 파일입니다.\n")
                print(f"'{attachment_path}' 예제 파일을 생성했습니다.")
            except Exception as e:
                print(f"예제 파일을 생성하는 데 실패했습니다: {e}")
                attachment_path = None # 파일 생성 실패 시 첨부하지 않음
        else:
            print(f"기존의 '{attachment_path}' 파일을 사용합니다.")

    # --- 3. MailServer 객체 생성 및 메일 발송 ---
    print("\nSMTP 서버에 연결을 시도합니다...")
    # --- 목적: 입력받은 정보로 MailServer 객체를 생성. 이 과정에서 서버 연결/로그인이 수행됩니다. ---
    mail_server = MailServer(sender_addr=sender_email, app_password=app_pw)
    
    # --- 목적: 서버 연결이 성공했을 경우에만 메일 발송을 시도 ---
    # MailServer 객체가 성공적으로 생성되었을 때(self.yag가 유효할 때)만 메일 발송을 시도합니다.
    if mail_server.yag:
        print("\n메일 발송을 시작합니다...")
        mail_server.send_email(
            receiver_addr=receiver_email,
            subject=mail_subject,
            body=mail_body,
            attachment=attachment_path
        )
