# log 파일의 경로.
LOG_PATH = 'dummy_sensor_values.log'

# 환경 변수명.
IN_TEMP = 'mars_base_internal_temperature'
EX_TEMP = 'mars_base_external_temperature'
HUMIDITY = 'mars_base_internal_humidity'
ILLUMINANCE = 'mars_base_external_illuminance'
CO2 = 'mars_base_internal_co2'
OXYGEN = 'mars_base_internal_oxygen'

import random

# 테스트를 위해 생성하는 환경 정보 클래스.
class DummySensor:
    # DummySensor 클래스 초기화.
    def __init__(self):
        # 화성 기지의 내부, 외부의 온도, 습도, 광량, 이산화탄소 농도, 산소 농도 초기화.
        self._env_values = {
            IN_TEMP: 0.0,
            EX_TEMP: 0.0,
            HUMIDITY: 0.0,
            ILLUMINANCE: 0.0,
            CO2: 0.0,
            OXYGEN: 0.0
        }
        # 화성 기지의 환경 값의 더미 데이터 생성을 위한 범위 값 지정.
        self._env_ranges = {
            IN_TEMP: (18, 30),
            EX_TEMP: (0, 21),
            HUMIDITY: (50, 60),
            ILLUMINANCE: (500, 715),
            CO2: (0.02, 0.1),
            OXYGEN: (4, 7)
        }

        # 날짜 및 시간 초기화.
        self._year = 2023 
        self._month = 8
        self._day = 27
        self._hour = 12
        self._minute = 0
        self._second = 0

        # log 파일 초기화.
        self._init_log()

    # 각 변수에 주어진 범위 내의 랜덤 값 설정(random.uniform 사용).
    def set_env(self):
        # 각 환경 변수에 범위를 지정해 실수로 저장.
        for key, range in self.__env_ranges.items():
            self.__env_values[key] = random.uniform(*range)

    # 랜덤 값으로 설정된 변수를 반환.
    def get_env(self):
        # timestamp 생성.
        timestamp = self._set_timestamp()
        # 환경 값을 로그로 변환.
        log_entity = f'{timestamp},' + ','.join(f'{value:.2f}' for value in self.__env_values.values()) + '\n'
        
        # log_entity를 log 파일에 저장.
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as log:
                log.write(log_entity)
        # 파일에 대한 접근 권한이 없을 경우,
        except PermissionError:
            print('ERROR: 파일의 접근 권한이 없습니다.')
        # 파일을 인코딩할 수 없을 경우,
        except UnicodeEncodeError:
            print('파일을 읽을 수 없습니다.')
        # 알 수 없는 오류가 발생할 경우,
        except Exception as error:
            print('ERROR: 알 수 없는 오류가 발생: ', error)

        return self.__env_values
    
    # 환경값을 저장하는 log 파일 초기화.
    def _init_log(self):
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as log:
                # 최초 파일 생성 시 헤더 생성.
                if log.tell() == 0:
                    headers = ['timestamp'] + list(self.__env_values.keys())
                    log.write(','.join(headers) + '\n')
        # 파일에 대한 접근 권한이 없을 경우,
        except PermissionError:
            print('ERROR: 파일의 접근 권한이 없습니다.')
        # 파일을 인코딩할 수 없을 경우,
        except UnicodeEncodeError:
            print('파일을 읽을 수 없습니다.')
        # 알 수 없는 오류가 발생할 경우,
        except Exception as error:
            print('ERROR: 알 수 없는 오류가 발생: ', error)

    # timestamp를 YYYY-MM-DD HH:MM:SS 형식으로 반환.
    def _set_timestamp(self):
        return f'{self.__year:04}-{self.__month:02}-{self.__day:02} {self.__hour:02}:{self.__minute:02}:{self.__second:02}'
    
    # 측정 시간 및 간격으로 반복 실행.
    def _increment_time(self, duration, interval):
        for _ in range(duration // interval):   
            self.set_env()
            self.get_env()
            self.__second += interval
            self.__update_time()

        print('----로그 파일 생성을 완료했습니다.----')

    # 시간 업데이트.
    def _update_time(self):
        if self.__second >= 60:
            self.__minute += self.__second
            self.__second %= 60
        if self.__minute >= 60:
            self.__hour += self.__minute
            self.__minute %= 60
        if self.__hour >= 24:
            self.__hour %= 24
            self.__update_day()

    # 날짜 업데이트.
    def _update_day(self):
        # 월별 일수.
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # 윤년 계산식.
        if (self.__year % 4 == 0 and self.__year % 100 != 0) or (self.__year % 400 == 0):
            days_in_month[2] = 29

        # 하루를 증가.
        self.__day += 1

        # 하루가 증가했을 때 매월 일수 비교.
        if self.__day > days_in_month[self.__month - 1]:
            self.__day = 1
            self.__month += 1
            if self.__month > 12:
                self.__month = 1
                self.__year += 1


# 실행 코드.
if __name__ == '__main__':
    # DummySensor 인스턴스 생성.
    ds = DummySensor()
    # 랜덤으로 생성되는 환경 변수 값 설정.
    ds.set_env()
    # 환경 변수 값 저장.
    env_data = ds.get_env()
    # 환경 변수 값 출력.
    for key, value in env_data.items():
        print(f"{key}: {value:.2f}")

    # 측정 시간 및 간격을 입력.
    duration = int(input('측정 시간을 초 단위로 입력하시오: '))
    interval = int(input('측정 간격을 초 단위로 입력하시오: '))

    ds._increment_time(duration, interval)