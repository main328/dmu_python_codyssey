import time
import threading
from dummy_sensor import DummySensor

# 환경 변수명 정의
IN_TEMP = 'mars_base_internal_temperature'
EX_TEMP = 'mars_base_external_temperature'
HUMIDITY = 'mars_base_internal_humidity'
ILLUMINANCE = 'mars_base_external_illuminance'
CO2 = 'mars_base_internal_co2'
OXYGEN = 'mars_base_internal_oxygen'

# MissionComputer 클래스 생성성
class MissionComputer:
    # 환경 변수에 대한 초기화.
    def __init__(self):
        self._env_values = {
            IN_TEMP: 0.0,
            EX_TEMP: 0.0,
            HUMIDITY: 0.0,
            ILLUMINANCE: 0.0,
            CO2: 0.0,
            OXYGEN: 0.0
        }
        # 5분 동안 환경 변수의 평균 값을 계산하기 위한 List
        self._data_log = []
        # 종료 플래그.
        self._stop_signal = False

    # 5초마다 환경 값을 갱신하고 5분마다 평균 값을 출력하는 함수.
    def get_sensor_data(self, sensor):
        start_time = time.time()
        input_thread = threading.Thread(target=self._check_stop, daemon=True)
        input_thread.start()
        
        while not self._stop_signal:
            sensor.set_env(self._env_values)
            self._env_values = sensor.get_env()

            print('\n----- 현재 환경 데이터 -----')
            for key, value in self._env_values.items():
                print(f'{key}: {value:.2f}')
            print('---------------------------')

            # 데이터 저장
            self._data_log.append(self._env_values.copy())

            # 5분(300초) 경과 시 평균값 출력
            if time.time() - start_time >= 300:
                self.print_five_minute_average()
                self._data_log.clear()
                start_time = time.time()

            # 5초 대기
            time.sleep(5)

        print('System stopped...')

    # 5분 동안 수집된 데이터를 환경 변수별로 평균 값을 계산하고 출력하는 함수.
    def print_five_minute_average(self):
        if not self._data_log:
            print('측정 간격이 5분이 되지 않아 평균값을 출력할 수 없습니다.')
            return

        avg_values = {key: 0.0 for key in self._env_values}
        total_entries = len(self._data_log)

        for data in self._data_log:
            for key in avg_values:
                avg_values[key] += data[key]

        for key in avg_values:
            avg_values[key] /= total_entries

        print('\n----- 5분간 평균 환경 데이터 -----')
        for key, value in avg_values.items():
            print(f'{key}: {value:.2f}')
        print('--------------------------------')

    # 사용자가 특정 값(Enter)을 입력하면 반복문을 종료하는 함수.
    def _check_stop(self):
        input("중지하려면 Enter 키를 입력하세요...\n")
        self._stop_signal = True


# 실행 코드
if __name__ == '__main__':
    ds = DummySensor()
    run_computer = MissionComputer()

    run_computer.get_sensor_data(ds)
