from selenium import webdriver # 웹 브라우저를 제어하는 핵심 도구입니다.
from selenium.webdriver.common.by import By # 웹 요소(element)를 어떤 기준으로 찾을지(ID, CSS 선택자 등) 지정합니다.
from selenium.webdriver.chrome.options import Options # 크롬 브라우저에 적용할 여러 옵션을 설정하는 클래스입니다.
from selenium.webdriver.support.ui import WebDriverWait # 특정 조건이 만족될 때까지 웹 드라이버가 기다리도록 하는 기능입니다. (명시적 대기)
from selenium.webdriver.support import expected_conditions as EC # WebDriverWait과 함께 사용되며, 기다려야 할 조건을 정의합니다. (예: 요소가 화면에 나타날 때까지)
from selenium.common.exceptions import TimeoutException, NoSuchElementException # 지정된 시간 내에 요소를 못 찾거나(Timeout), 요소가 아예 없을 때(NoSuchElement) 발생하는 예외를 처리하기 위해 사용합니다.

class Crawling:
    """
    네이버 자동 로그인 및 정보 크롤링을 담당하는 클래스입니다.
    이 클래스는 웹 드라이버 초기화, 쿠키를 이용한 로그인, 정보 수집, 종료 과정을 체계적으로 관리합니다.
    """
    
    # 1. 클래스 초기 설정
    def __init__(self):
        """
        Crawling 클래스가 생성될 때 가장 먼저 실행되는 초기화 메서드(생성자)입니다.
        크롬 프로필 경로를 설정하고, 웹 드라이버를 초기화하여 `self.driver`에 할당합니다.
        """
        # [중요] 크롬 사용자 프로필 경로 설정. 여기에 로그인 정보(쿠키)가 저장됩니다.
        # r'' 형태는 경로 문자열의 '\'를 이스케이프 문자로 해석하지 않도록 합니다.
        self.profile_path = r'C:\Deveopment\School\dmu_python_codyssey\pbl_mission004\user_data'
        # 웹 드라이버를 초기화하고 실행하는 메서드를 호출합니다.
        self.driver = self._init_web_driver()

    # 2. 웹 드라이버 초기 설정
    def _init_web_driver(self):
        """
        Selenium 웹 드라이버(크롬)를 설정하고 생성하는 내부 메서드입니다.
        Args:
            None
        Returns:
            webdriver.Chrome: 모든 설정이 적용된 크롬 웹 드라이버 객체.
        """
        # 웹사이트가 크롤러를 봇으로 인식하지 않도록 일반적인 브라우저의 User-Agent 정보를 설정합니다.
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        print(f'[INFO] User-Agent 설정: {user_agent}')

        # 크롬 브라우저에 적용할 옵션을 생성합니다.
        web_option = Options()
        # User-Agent 정보를 옵션에 추가합니다.
        web_option.add_argument(f'user-agent={user_agent}')
        # [핵심] 사용자 데이터 디렉터리를 지정합니다. 이 경로에 쿠키, 로그인 세션 등이 저장되어
        # 프로그램 재실행 시 자동 로그인이 가능하게 됩니다.
        web_option.add_argument(f'user-data-dir={self.profile_path}')
        # 시스템 환경(특히 리눅스 서버)에서 발생할 수 있는 충돌을 방지하기 위한 옵션입니다.
        web_option.add_argument("--no-sandbox") # 샌드박스 보안 기능 비활성화
        web_option.add_argument("--disable-dev-shm-usage") # 공유 메모리 사용 비활성화
        print(f'[INFO] Web_Option 설정 완료.')

        # 설정한 옵션을 적용하여 크롬 웹 드라이버를 실행합니다.
        driver = webdriver.Chrome(options=web_option)
        # [암시적 대기] 요소를 찾을 때, 해당 요소가 즉시 없으면 최대 5초까지 기다립니다.
        # 이 시간 안에 요소가 나타나면 바로 다음 코드를 실행합니다.
        driver.implicitly_wait(5)

        return driver
    
    # 3. 쿠키를 이용한 로그인 처리
    def _set_login_with_cookie(self):
        """
        저장된 쿠키(세션)를 이용해 자동 로그인을 시도하고, 실패 시 수동 로그인을 유도하는 메서드입니다.
        """
        # 먼저 네이버 메인 페이지로 이동합니다.
        self.driver.get('https://www.naver.com')

        try:
            # [명시적 대기] 5초 동안 로그인 시 나타나는 '닉네임' 요소가 있는지 확인합니다.
            # 이 요소가 있으면 이미 로그인된 상태로 판단합니다.
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.MyView-module__nickname___fcxwI'))
            )
            print('[INFO] 자동 로그인 상태를 확인했습니다.')
        except TimeoutException:
            # 5초 안에 닉네임 요소를 찾지 못하면 TimeoutException이 발생하며, 이는 로그인이 안 된 상태입니다.
            # 최초 실행이거나 쿠키가 만료된 경우에 해당합니다.
            print('[INFO] 수동 로그인이 필요합니다. 로그인 페이지로 이동합니다...')
            self.driver.get('https://nid.naver.com/nidlogin.login')
            # 사용자가 직접 로그인하고 Enter를 누를 때까지 프로그램 실행을 잠시 멈춥니다.
            input('[INFO] 브라우저에서 수동 로그인을 완료한 후, Enter 키를 입력해주세요...')
            
            # 수동 로그인이 정말 성공했는지 다시 한번 확인합니다.
            self.driver.get('https://www.naver.com')
            try:
                # 다시 5초간 닉네임 요소가 나타나는지 확인합니다.
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.MyView-module__nickname___fcxwI')))
                print('[INFO] 수동 로그인이 성공적으로 완료되었습니다.')
            except TimeoutException:
                # 수동 로그인 후에도 닉네임 요소를 찾지 못했다면 로그인에 최종 실패한 것입니다.
                # 이 경우, 에러를 발생시켜 프로그램을 즉시 종료합니다.
                raise ValueError('[ERROR] 수동 로그인에 실패했습니다. 프로그램을 종료합니다.')
    
    # 4. 네이버 메인 페이지 정보 크롤링
    def _crawl_main_page_info(self):
        """
        로그인 후 네이버 메인 페이지에서 사용자 닉네임과 이메일 주소를 크롤링합니다.
        Returns:
            dict: 크롤링된 사용자 정보 {'nickname': '...', 'email': '...'}.
        """
        crawled_data = {} # 크롤링한 데이터를 저장할 빈 딕셔너리
        print('\n[INFO] 사용자 정보 크롤링을 시작합니다.')
        try:
            # 먼저 닉네임과 이메일을 포함하는 더 큰 영역('account' ID를 가진 요소)을 찾습니다.
            # 이 영역이 10초 내에 나타날 때까지 기다립니다.
            account_info_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'account'))
            )
            print('[SUCCESS] 사용자 정보 영역을 성공적으로 찾았습니다.')

            # 위에서 찾은 영역 안에서 닉네임 요소를 찾습니다.
            try:
                nickname_element = account_info_area.find_element(By.CSS_SELECTOR, '.MyView-module__nickname___fcxwI')
                crawled_data['nickname'] = nickname_element.text # 요소의 텍스트(닉네임)를 추출하여 저장
                print(f"닉네임: {crawled_data['nickname']}")
            except NoSuchElementException:
                print("[FAIL] 닉네임을 찾는 데 실패했습니다.")

            # 같은 영역 안에서 이메일 요소를 찾습니다.
            try:
                email_element = account_info_area.find_element(By.CSS_SELECTOR, '.MyView-module__desc_email___JwAKa')
                crawled_data['email'] = email_element.text # 요소의 텍스트(이메일)를 추출하여 저장
                print(f"이메일: {crawled_data['email']}")
            except NoSuchElementException:
                print("[FAIL] 이메일을 찾는 데 실패했습니다.")
        
        except TimeoutException:
            # 'account' 영역 자체를 시간 내에 찾지 못한 경우
            print('[ERROR] 로그인 후 사용자 정보 영역을 시간 내에 찾지 못했습니다.')
        except Exception as e:
            # 그 외 예상치 못한 다른 오류가 발생한 경우
            print(f'[ERROR] 메인 페이지 크롤링 중 오류가 발생했습니다: {e}')
        
        return crawled_data

    # 5. 네이버 메일 제목 크롤링 (보너스 과제)
    def _crawl_mail_subjects(self):
        """
        네이버 메일 페이지로 이동하여 받은메일함 첫 페이지의 메일 제목들을 크롤링합니다.
        Returns:
            list: 크롤링된 메일 제목 문자열들이 담긴 리스트.
        """
        mail_subjects = [] # 메일 제목들을 저장할 빈 리스트
        print('\n[INFO] 네이버 메일 페이지로 이동합니다...')
        self.driver.get('https://mail.naver.com/')

        try:
            # 메일 목록 전체를 감싸는 'mail_list_wrap' 요소가 나타날 때까지 최대 10초 기다립니다.
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "mail_list_wrap"))
            )
            print("[SUCCESS] 메일 목록 로딩을 확인했습니다.")

            # 메일 제목에 해당하는 모든 요소를 리스트 형태로 가져옵니다. (find_elements는 복수형)
            subject_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.mail_title span.text')
            
            # 메일 제목 요소를 하나도 찾지 못했는지 확인합니다.
            if not subject_elements:
                print("[FAIL] 메일 제목을 찾을 수 없습니다.")
            else:
                # 찾은 모든 제목 요소에 대해 반복 작업을 수행합니다.
                for element in subject_elements:
                    # 요소의 텍스트(메일 제목)가 비어있지 않은 경우에만 리스트에 추가합니다.
                    if element.text:
                        mail_subjects.append(element.text)
                print(f"[SUCCESS] 총 {len(mail_subjects)}개의 메일 제목을 성공적으로 가져왔습니다.")

        except TimeoutException:
            print("[ERROR] 메일 페이지가 시간 내에 로딩되지 않았거나, 로그인에 실패했을 수 있습니다.")
        except Exception as e:
            print(f"[ERROR] 메일 제목 크롤링 중 오류가 발생했습니다: {e}")

        return mail_subjects

    # 6. 전체 크롤링 프로세스 실행
    def run(self):
        """
        정의된 모든 크롤링 단계를 순서대로 실행하는 메인 메서드입니다.
        Returns:
            tuple: (메인 페이지 정보 딕셔너리, 메일 제목 리스트)
        """
        self._set_login_with_cookie()       # 1단계: 로그인 처리
        main_page_data = self._crawl_main_page_info()   # 2단계: 메인 페이지 정보 수집
        mail_subjects_data = self._crawl_mail_subjects() # 3단계: 메일 제목 수집
        return main_page_data, mail_subjects_data

    # 7. 드라이버 종료
    def close(self):
        """
        모든 작업이 끝난 후 웹 드라이버를 종료하여 관련 프로세스와 리소스를 정리합니다.
        """
        # 드라이버가 실행 중인 상태일 때만 종료 명령을 내립니다.
        if self.driver:
            self.driver.quit() # 브라우저 창과 백그라운드 프로세스를 모두 종료합니다.
            print('\n[INFO] 모든 작업을 완료하고 브라우저를 종료했습니다.')

# [프로그램 실행 부분]
# 이 스크립트 파일이 직접 실행될 때만 아래 코드가 동작하도록 합니다.
if __name__ == "__main__":
    # Crawling 클래스의 인스턴스(객체)를 생성합니다. 이 때 __init__ 메서드가 자동 호출됩니다.
    crawling = Crawling()

    try:
        # run 메서드를 호출하여 전체 크롤링 프로세스를 실행하고, 결과를 두 변수에 나눠 받습니다.
        main_info, mail_subjects = crawling.run()

        # [최종 결과 출력]
        print('\n--- 기본 과제 크롤링 결과 ---')
        if not main_info:
            print('가져온 내용이 없습니다.')
        else:
            # 문제에서 요구한 리스트 형태로 감싸서 출력합니다.
            result_list = [main_info]
            print(result_list)

        print('\n--- 보너스 과제 크롤링 결과 (메일 제목) ---')
        if not mail_subjects:
            print('가져온 메일 제목이 없습니다.')
        else:
            print(mail_subjects)
            
    except Exception as e:
        # 크롤링 과정 중 어느 단계에서든 예외(에러)가 발생하면 여기서 처리합니다.
        print(f"\n[CRITICAL ERROR] 크롤링 프로세스 중 에러가 발생하여 종료합니다: {e}")
    finally:
        # [중요] try 블록의 코드가 성공하든, 예외가 발생하여 실패하든 상관없이
        # finally 블록은 '항상' 실행됩니다.
        # 이를 통해 어떤 상황에서든 브라우저가 안전하게 종료되도록 보장합니다.
        crawling.close()