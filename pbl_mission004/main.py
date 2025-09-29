import os # [수정] 안정적인 파일 경로를 위해 os 모듈을 import 합니다.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Crawling:
    # Crawling 클래스 초기 설정.
    def __init__(self):
        '''
        Args:
        Returns:
        '''

        self.profile_path = r'C:\Deveopment\School\dmu_python_codyssey\pbl_mission004\user_data'
        self.driver = self._init_web_driver()

    # 웹 드라이버 초기 설정.
    def _init_web_driver(self):
        '''
        Args:
            None
        Returns:
            web_driver(webdriver.chrome): 초기 설정된 Selenium 웹 드라이버.
        '''
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        print(f'[INFO] User-Agent 설정: {user_agent}')

        web_option = Options()
        # 웹 브라우저의 정보를 지정.
        web_option.add_argument(f'user-agent={user_agent}')
        # 웹 브라우저의 사용자 정보를 지정.
        web_option.add_argument(f'user-data-dir={self.profile_path}')
        # 웹 브라우저의 충돌 방지를 위한 샌드박스 보안 기능 우회.
        web_option.add_argument("--no-sandbox")
        # 웹 브라우저의 충돌 방지를 위한 공유 메모리 비활성화.
        web_option.add_argument("--disable-dev-shm-usage")
        print(f'[INFO] Web_Option 설정 완료.') # [수정] Options 객체 자체를 출력하면 너무 길어지므로 간단한 메시지로 변경합니다.

        driver = webdriver.Chrome(options=web_option)
        driver.implicitly_wait(5)

        return driver
    
    def _set_login_with_cookie(self):
        '''
        Args:
        Returns:
        '''
        self.driver.get('https://www.naver.com')

        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.MyView-module__nickname___fcxwI'))
            )
            print('[INFO] 자동 로그인 상태를 확인.')
        except TimeoutException:
            # 최초 실행일 경우, 수동 로그인 진행.
            print('[INFO] 수동 로그인을 진행 중...')
            self.driver.get('https://nid.naver.com/nidlogin.login')
            input('[INFO] 수동 로그인 완료 시 Enter키 입력...')
            
            # 수동 로그인 성공 여부 확인.
            self.driver.get('https://www.naver.com')
            try:
                # [수정] WebDriverWait은 성공 시 요소를 반환하고, 실패 시 TimeoutException을 발생시킵니다.
                # 따라서 불필요한 if 조건문 없이, 이 구문이 예외 없이 통과되면 성공으로 간주하는 것이 올바른 로직입니다.
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.MyView-module__nickname___fcxwI')))
                print('[INFO] 수동 로그인 성공.')
            except TimeoutException:
                # 최종적으로 로그인에 실패할 경우, 프로그램 종료.
                raise ValueError('[INFO] 수동 로그인 실패로 프로그램을 종료.')
        
    def _crawl_main_page_info(self):
        """
        로그인 후 메인 페이지의 사용자 정보를 크롤링합니다.

        Returns:
            dict: 크롤링된 사용자 정보 (닉네임, 이메일).
        """
        crawled_data = {}
        print('\n사용자 정보 크롤링을 시작합니다.')
        try:
            account_info_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'account'))
            )
            print('사용자 정보 영역을 성공적으로 찾았습니다.')

            try:
                nickname_element = account_info_area.find_element(By.CSS_SELECTOR, '.MyView-module__nickname___fcxwI')
                crawled_data['nickname'] = nickname_element.text
                print(f"닉네임: {crawled_data['nickname']}")
            except NoSuchElementException:
                print("닉네임을 찾는 데 실패했습니다.")

            try:
                email_element = account_info_area.find_element(By.CSS_SELECTOR, '.MyView-module__desc_email___JwAKa')
                crawled_data['email'] = email_element.text
                print(f"이메일: {crawled_data['email']}")
            except NoSuchElementException:
                print("이메일을 찾는 데 실패했습니다.")
        
        except TimeoutException:
            print('오류: 로그인 후 사용자 정보 영역을 시간 내에 찾지 못했습니다.')
        except Exception as e:
            print(f'메인 페이지 크롤링 중 오류가 발생했습니다: {e}')
        
        return crawled_data

    def _crawl_mail_subjects(self):
        """
        네이버 메일 페이지로 이동하여 메일 제목을 크롤링합니다.

        Returns:
            list: 크롤링된 메일 제목들의 리스트.
        """
        mail_subjects = []
        print('\n[보너스 과제] 네이버 메일 페이지로 이동합니다...')
        self.driver.get('https://mail.naver.com/')

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "mail_list_wrap"))
            )
            print("메일 목록 로딩을 확인했습니다.")

            subject_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.mail_title span.text')
            
            if not subject_elements:
                print("메일 제목을 찾을 수 없습니다.")
            else:
                for element in subject_elements:
                    if element.text:
                        mail_subjects.append(element.text)
                print(f"총 {len(mail_subjects)}개의 메일 제목을 성공적으로 가져왔습니다.")

        except TimeoutException:
            print("오류: 메일 페이지가 시간 내에 로딩되지 않았거나, 로그인에 실패했습니다.")
        except Exception as e:
            print(f"메일 제목 크롤링 중 오류가 발생했습니다: {e}")

        return mail_subjects

    def run(self):
        """
        전체 크롤링 프로세스를 실행합니다.

        Returns:
            tuple: 메인 페이지 정보(dict)와 메일 제목 리스트(list)를 담은 튜플.
        """
        self._set_login_with_cookie()
        main_page_data = self._crawl_main_page_info()
        mail_subjects_data = self._crawl_mail_subjects()
        return main_page_data, mail_subjects_data

    def close(self):
        """
        웹 드라이버를 종료합니다.
        """
        if self.driver:
            self.driver.quit()
            print('\n모든 작업을 완료하고 브라우저를 종료했습니다.')

if __name__ == "__main__":
    crawling = Crawling()

    try:
        # [수정] crawling.run()을 직접 호출하기 전에 로그인 설정을 먼저 수행해야 합니다.
        # run 메서드 내부에서 호출하도록 순서를 변경합니다.
        main_info, mail_subjects = crawling.run()

        # 4. 최종 결과 출력
        print('\n--- 기본 과제 크롤링 결과 ---')
        if not main_info:
            print('가져온 내용이 없습니다.')
        else:
            result_list = [main_info]
            print(result_list)

        print('\n--- 보너스 과제 크롤링 결과 (메일 제목) ---')
        if not mail_subjects:
            print('가져온 메일 제목이 없습니다.')
        else:
            print(mail_subjects)
            
    except Exception as e:
        print(f"\n크롤링 프로세스 중 에러가 발생하여 종료합니다: {e}")
    finally:
        crawling.close()
