# -*- coding: utf-8 -*-
"""
파일 목적: yagmail 라이브러리를 사용하여 Gmail 이메일을 간편하게 발송하는 스크립트입니다.
           HTML 본문, CSV 파일 연동, 다중 발송(개별/일괄) 기능을 지원합니다.

주요 기능:
1. 스크립트 실행 시 사용자로부터 Gmail 계정과 앱 비밀번호를 입력받아 SMTP 서버에 접속합니다.
2. 'mail_target_list.csv' 파일에서 (미리 작성된) 수신자 명단을 읽어옵니다.
3. 지정된 수신자들에게 HTML 형식의 이메일과 첨부 파일을 발송합니다.
4. 발송 방식을 (1) 개별 반복 발송 또는 (2) 전체 숨은 참조(BCC) 발송 중 선택할 수 있습니다.

사용 전 필수사항:
- `pip install yagmail` 명령어로 yagmail 라이브러리를 설치해야 합니다.
- 'mail_target_list.csv' 파일이 스크립트와 동일한 경로에 미리 작성되어 있어야 합니다.
- 발신자로 사용할 Gmail 계정의 '2단계 인증'이 활성화되어 있어야 합니다.
- Google 계정 설정에서 '앱 비밀번호' (16자리)를 생성해야 합니다.
"""

# --- 모듈 임포트 ---
import yagmail
import os
import csv

class MailServer:
    """
    yagmail을 사용하여 SMTP 서버와의 연결 및 메일 발송을 관리하는 클래스입니다.
    Gmail('smtp.gmail.com') 및 Naver('smtp.naver.com') 등 호스트 지정이 가능합니다.
    """
    def __init__(self, sender_addr, app_password, host='smtp.gmail.com'):
        """
        MailServer 인스턴스를 초기화하고 SMTP 서버에 로그인합니다.

        Args:
            sender_addr (str): 보내는 사람의 이메일 주소.
            app_password (str): 계정의 16자리 앱 비밀번호.
            host (str, optional): 접속할 SMTP 서버 호스트. 기본값은 'smtp.gmail.com'.
        """
        self.sender_addr = sender_addr
        
        try:
            self.yag = yagmail.SMTP(user=sender_addr, password=app_password, host=host)
            print(f"[INFO] '{sender_addr}' 계정으로 '{host}' 서버에 성공적으로 연결되었습니다.")
        except Exception as e:
            print(f"[오류] SMTP 서버 연결 또는 로그인에 실패했습니다: {e}")
            print("- 계정 주소와 16자리 앱 비밀번호가 정확한지 확인해주세요.")
            self.yag = None

    def send_email(self, subject, body, to=None, cc=None, bcc=None, attachment=None):
        """
        초기화된 SMTP 연결을 사용하여 이메일을 발송합니다. (HTML 지원)

        Args:
            subject (str): 이메일의 제목.
            body (str or list): 이메일의 본문 내용. 
                                HTML로 보내려면 반드시 리스트 [html_string] 형태로 전달해야 합니다.
            to (str or list, optional): 받는 사람의 이메일 주소.
            cc (str or list, optional): 참조 (CC) 이메일 주소.
            bcc (str or list, optional): 숨은 참조 (BCC) 이메일 주소.
            attachment (str or list, optional): 첨부할 파일의 경로.

        Returns:
            bool: 메일 발송 성공 시 True, 실패 시 False를 반환합니다.
        """
        if not self.yag:
            print("[오류] SMTP 서버가 연결되어 있지 않아 메일을 보낼 수 없습니다.")
            return False
        
        if not to and not cc and not bcc:
            print("[오류] 수신자(to, cc, bcc)가 아무도 지정되지 않았습니다.")
            return False
            
        try:
            # yagmail은 contents(여기서는 body)가 list 형태이면 HTML 원본으로 처리합니다.
            self.yag.send(
                to=to,
                subject=subject,
                contents=body,
                attachments=attachment,
                cc=cc,
                bcc=bcc
            )
            
            targets = []
            if to:
                targets.append(f"To: {to if isinstance(to, str) else len(to) }")
            if cc:
                targets.append(f"CC: {to if isinstance(cc, str) else len(cc) }")
            if bcc:
                targets.append(f"BCC: {to if isinstance(bcc, str) else len(bcc) }명")
            
            print(f"[성공] 메일을 성공적으로 발송했습니다. ({', '.join(targets)})")
            return True
        except Exception as e:
            print(f"[오류] 메일 발송 중 문제가 발생했습니다: {e}")
            return False

def load_recipients_from_csv(filename='mail_target_list.csv'):
    """
    미리 작성된 CSV 파일에서 수신자 명단(이름, 이메일)을 읽어 리스트로 반환합니다.
    
    Args:
        filename (str): 읽어올 CSV 파일 이름.

    Returns:
        list: (이름, 이메일) 형태의 튜플 리스트. [('이름1', '메일1'), ...]
    """
    recipients = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # 헤더 행(이름, 이메일) 건너뛰기
            
            for row in reader:
                if row and len(row) >= 2:
                    name = row[0].strip()
                    email = row[1].strip()
                    if name and email:
                        recipients.append((name, email))
                        
            if not recipients:
                print(f"[경고] '{filename}' 파일에 유효한 수신자 명단이 없습니다.")
                
            return recipients
            
    except FileNotFoundError:
        print(f"[오류] 수신자 명단 파일('{filename}')을 찾을 수 없습니다.")
        print("스크립트와 동일한 경로에 'mail_target_list.csv' 파일을 생성해주세요.")
        return []
    except Exception as e:
        print(f"[오류] CSV 파일 읽기 중 오류가 발생했습니다: {e}")
        return []

def get_html_body(recipient_name=None):
    """
    화성 고립 상황을 알리는 HTML 형식의 이메일 본문을 생성합니다.
    수신자 이름이 주어지면 개인화된 인사를 포함합니다.

    Args:
        recipient_name (str, optional): 메일 본문에 포함할 수신자 이름.

    Returns:
        str: HTML 형식의 이메일 본문 문자열.
    """
    
    greeting = f'안녕하십니까, {recipient_name}님,' if recipient_name else '안녕하십니까,'

    # f-string 내부의 CSS { }는 {{ }}로 이스케이프 처리해야 합니다.
    html_body = f"""
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        <div class='container'>
            <div class='header'>[긴급] 화성 생존자 구조 요청 - Dr. Han</div>
            <div class='content'>
                <p>{greeting}</p>
                <p>저는 화성 탐사선 '아레스 5'의 대원 <b>한송희</b>입니다.<br>
                   임무 중 발생한 예기치 못한 사고로 현재 화성에 고립되어 있습니다.</p>
                <p>방금 지구와의 통신이 복구되었습니다. 이 메시지는 저의 생존을 알리고 
                   <span class='highlight'>즉각적인 구조를 요청</span>하기 위함입니다.</p>
                <p>현재 저의 정확한 위치, 기지 상태, 잔여 보급품에 대한 상세 데이터는 
                   첨부된 'report.txt' 파일을 확인해 주시기 바랍니다.</p>
                <p style='font-size: 18px; font-weight: bold; color: #d9534f;'>
                   여러분의 도움이 절실히 필요합니다. 조속한 회신 부탁드립니다.
                </p>
            </div>
            <div class='footer'>
                <p>-- <br>
                   Dr. Song-Hee Han<br>
                   Ares V Mission Specialist<br>
                   Location: Mars, Acidalia Planitia
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_body

def create_dummy_attachment(filename='report.txt'):
    """
    첨부할 예제 'report.txt' 파일이 없으면 생성합니다.
    
    Args:
        filename (str): 생성할 첨부 파일 이름.
    """
    attachment_path = filename
    if not os.path.exists(attachment_path):
        print(f"[INFO] 예제 첨부 파일 '{attachment_path}'을 생성합니다.")
        try:
            with open(attachment_path, 'w', encoding='utf-8') as f:
                f.write("--- 화성 기지 상태 보고서 (ARES V) ---\n")
                f.write(f"보고자: 한송희 (Dr. Han)\n")
                f.write("상태: 생존. 기지 일부 파손되었으나 생명 유지 장치 작동 중.\n")
                f.write("식량: 약 60일분 잔여.\n")
                f.write("통신: 주 통신망 파괴. 보조 송신기 간헐적 작동.\n")
                f.write("요청: 즉각적인 구조 및 보급 필요.\n")
        except Exception as e:
            print(f"예제 파일을 생성하는 데 실패했습니다: {e}")
            return None
    else:
        print(f"기존의 '{attachment_path}' 파일을 첨부 파일로 사용합니다.")
    return attachment_path

# --- 목적: 스크립트의 메인 실행 블록 정의 ---
if __name__ == "__main__":
    
    csv_filename = 'mail_target_list.csv'
    recipients_list = load_recipients_from_csv(csv_filename)
    
    if not recipients_list:
        print(f"[종료] '{csv_filename}'에 발송할 대상이 없거나 파일을 찾을 수 없습니다.")
    else:
        print(f"\n--- 총 {len(recipients_list)}명의 수신자를 불러왔습니다 ---")
        for i, (name, email) in enumerate(recipients_list):
            print(f"  {i+1}. {name} ({email})")

        print("\n--- 이메일 발송 정보 입력 ---")
        sender_email = input("보내는 사람의 Gmail 주소 (예: user@gmail.com): ")
        
        print("\n[중요] Google 계정의 '앱 비밀번호' 16자리를 입력해야 합니다.")
        app_pw = input("Gmail 앱 비밀번호: ")

        mail_subject = input("\n메일 제목 (예: [긴급] 구조 요청): ")

        attachment_path = create_dummy_attachment('report.txt')

        print("\nSMTP 서버에 연결을 시도합니다...")
        mail_server = MailServer(sender_addr=sender_email, app_password=app_pw)
        
        if mail_server.yag:
            print("\n--- 발송 방식 선택 ---")
            print("1: [개별 발송] 수신자 개개인에게 맞춤 메일을 보냅니다. (수신자는 본인만 보임)")
            print("2: [전체 발송] 모든 수신자를 '숨은 참조(BCC)'로 하여 한 번에 보냅니다. (수신자들은 서로를 볼 수 없음)")
            choice = input("원하는 발송 방식의 번호를 입력하세요 (1 또는 2): ")

            if choice == '1':
                print("\n--- [방식 1] 개별 반복 발송을 시작합니다 ---")
                success_count = 0
                for name, email in recipients_list:
                    print(f"-> '{name}' ({email}) 님에게 발송 시도...")
                    personalized_body = get_html_body(recipient_name=name)
                    
                    # --- [수정됨] ---
                    # body를 [personalized_body] 리스트로 감싸서 HTML 원본으로 보냅니다.
                    if mail_server.send_email(
                        subject=mail_subject,
                        body=[personalized_body], # <-- 수정된 부분
                        to=email,
                        attachment=attachment_path
                    ):
                        success_count += 1
                
                print(f"\n[발송 완료] 총 {len(recipients_list)}명 중 {success_count}명에게 성공적으로 발송했습니다.")

            elif choice == '2':
                print("\n--- [방식 2] 전체 BCC 발송을 시작합니다 ---")
                
                email_addresses_only = [email for name, email in recipients_list]
                general_body = get_html_body(recipient_name=None)
                
                # --- [수정됨] ---
                # body를 [general_body] 리스트로 감싸서 HTML 원본으로 보냅니다.
                mail_server.send_email(
                    subject=mail_subject,
                    body=[general_body], # <-- 수정된 부분
                    to=mail_server.sender_addr, 
                    bcc=email_addresses_only,
                    attachment=attachment_path
                )

            else:
                print("[오류] '1' 또는 '2'만 입력해야 합니다. 발송을 취소합니다.")
        
        else:
            print("[종료] SMTP 서버 연결에 실패하여 메일 발송을 진행할 수 없습니다.")