# requests: 웹 페이지의 HTML을 가져오기 위한 라이브러리
# BeautifulSoup: HTML 코드를 파싱(parsing)하여 원하는 데이터를 쉽게 추출하도록 도와주는 라이브러리
import requests
from bs4 import BeautifulSoup

# --- 클래스 정의 ---
# PEP 8 가이드라인에 따라 클래스 이름은 각 단어의 첫 글자를 대문자로 쓰는 CapWords(PascalCase) 방식을 권장합니다.
class Crawling:
    """
    KBS 뉴스 웹사이트의 헤드라인 뉴스를 수집(크롤링)하는 기능을 담당하는 클래스입니다.

    이 클래스는 지정된 URL에 접속하여 HTML을 분석하고,
    헤드라인 뉴스의 제목과 링크를 추출하여 파일로 저장하는 역할을 합니다.
    """

    # --- 초기화 메서드 ---
    def __init__(self):
        """
        Crawling 클래스의 인스턴스(객체)를 생성할 때 초기 설정을 담당합니다.

        Args:
            None

        Returns:
            None
        """
        # --- 인스턴스 변수(속성) 정의 ---
        # 크롤링할 웹사이트의 기본 주소. 상대 경로 링크를 절대 경로로 만들 때 사용됩니다.
        self._base_url = 'https://news.kbs.co.kr'
        # 크롤링 대상 페이지의 전체 주소. f-string을 사용하여 기본 주소와 결합합니다.
        self._url = f'{self._base_url}/news/pc/main/main.html'
        # 웹사이트 응답 대기 시간(초). 이 시간 안에 응답이 없으면 예외가 발생합니다.
        self._timeout = 5
        # 추출된 헤드라인 데이터를 저장할 리스트. [{'index':..., 'title':..., 'link':...}] 형태로 저장됩니다.
        self._headline_list = []

    # --- 메인 크롤링 메서드 ---
    def get_crawling_headline(self):
        """
        지정된 URL에서 헤드라인 뉴스를 크롤링하여 리스트에 저장하고, 파일로 저장하는 메서드를 호출합니다.

        Args:
            None

        Returns:
            None
        """
        # --- 예외 처리 블록 ---
        # 네트워크 오류나 데이터 처리 중 예기치 못한 문제 발생에 대비합니다.
        try:
            # 1. HTTP GET 요청 보내기
            # requests.get() 함수를 사용하여 지정된 URL의 웹 페이지 내용을 요청합니다.
            # timeout 인자를 설정하여 서버의 응답을 무한정 기다리지 않도록 합니다.
            response = requests.get(url=self._url, timeout=self._timeout)
            
            # 2. HTTP 응답 상태 코드 검사
            # .raise_for_status()는 응답 코드가 200(성공)이 아닐 경우, HTTPError 예외를 발생시킵니다.
            # 이를 통해 요청이 실패했음을 즉시 알 수 있습니다.
            response.raise_for_status()

            # 3. HTML 파싱
            # BeautifulSoup 객체를 생성합니다.
            # response.text는 응답받은 HTML 소스 코드이며, 'html.parser'는 내장된 기본 파서를 사용하겠다는 의미입니다.
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 4. 원하는 데이터 선택
            # CSS 선택자를 사용하여 원하는 HTML 요소를 찾습니다.
            # 'a[aria-label="헤드라인 링크"]'는 aria-label 속성값이 "헤드라인 링크"인 모든 <a> 태그를 선택합니다.
            news_items = soup.select('a[aria-label="헤드라인 링크"]')

            # 5. 데이터 존재 여부 확인
            # 크롤링한 결과가 없는 경우(웹사이트 구조 변경 등) 사용자에게 알리고 함수를 종료합니다.
            if not news_items:
                print('헤드라인 뉴스를 찾을 수 없습니다. 웹사이트 구조를 확인하세요.')
                return 

            # 6. 데이터 순회 및 추출
            # enumerate() 함수를 사용하여 각 뉴스 아이템에 1부터 시작하는 번호를 부여합니다.
            for index, item in enumerate(news_items, 1):
                # 각 뉴스 아이템(<a> 태그) 내에서 제목이 들어있는 <p class="title"> 태그를 찾습니다.
                title_tag = item.select_one('p.title')
                
                # 간혹 구조상 제목 태그가 없는 아이템이 있을 수 있으므로, 확인 후 다음 아이템으로 넘어갑니다.
                if not title_tag:
                    continue

                # .get_text(strip=True)를 사용하여 태그 안의 텍스트만 추출하고, 양쪽의 공백을 모두 제거합니다.
                title = title_tag.get_text(strip=True)
                # <a> 태그의 href 속성값(상대 경로)을 가져와 기본 URL과 합쳐 완전한 URL을 만듭니다.
                link = self._base_url + item['href']

                # 7. 추출한 데이터 저장
                # .append() 메서드를 사용하여 인스턴스 변수 리스트에 데이터를 추가합니다.
                # 딕셔너리 형태로 저장하면 'title', 'link' 키로 데이터에 쉽게 접근할 수 있어 관리가 편합니다.
                self._headline_list.append({'index': index, 'title': title, 'link': link})
            
            # 8. 파일 저장 메서드 호출
            # 데이터 추출이 모두 성공적으로 끝나면, 결과를 파일로 저장하는 메서드를 호출합니다.
            print(f'총 {len(self._headline_list)}개의 헤드라인을 찾았습니다. 파일로 저장합니다.')
            self.save_to_file()

        # --- 예외 처리 ---
        # requests 라이브러리에서 발생하는 네트워크 관련 예외를 처리합니다.
        except requests.exceptions.RequestException as error:
            print(f'HTTP 요청 중 오류 발생: {error}')
        # 그 외 모든 종류의 예외를 처리하여 프로그램이 갑자기 중단되는 것을 방지합니다.
        except Exception as error:
            print(f'처리 중 오류 발생: {error}')
            
    # --- 파일 저장 메서드 ---
    def save_to_file(self):
        """
        인스턴스 변수 _headline_list에 저장된 데이터를 텍스트 파일로 저장합니다.

        Args:
            None

        Returns:
            None
        """
        # with open(...) 구문을 사용하면 파일을 사용한 후 자동으로 닫아주어 편리합니다.
        # 'w'는 쓰기 모드, encoding='utf-8'은 한글이 깨지지 않도록 설정하는 것입니다.
        with open('headline_news.txt', 'w', encoding='utf-8') as f:
            # 리스트에 저장된 각 뉴스(딕셔너리)를 순회합니다.
            for news in self._headline_list:
                # f-string을 사용하여 정해진 형식으로 파일에 내용을 씁니다.
                # \n은 줄바꿈을 의미합니다.
                f.write(f"[{news['index']}]\n")
                f.write(f"제목: {news['title']}\n")
                f.write(f"링크: {news['link']}\n\n")
        print('파일 저장 완료: headline_news.txt')


# --- 스크립트 실행 시작점 ---
# 이 스크립트 파일이 직접 실행될 때만 아래 코드가 동작하도록 하는 파이썬의 표준적인 방법입니다.
# 다른 파일에서 이 파일을 import할 경우에는 아래 코드가 실행되지 않습니다.
if __name__ == '__main__':
    # Crawling 클래스를 기반으로 실제 동작할 객체(인스턴스)를 생성합니다.
    crawler = Crawling()
    # 생성된 객체의 get_crawling_headline 메서드를 호출하여 크롤링을 시작합니다.
    crawler.get_crawling_headline()