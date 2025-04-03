import random

# 환경 변수명
IN_TEMP = 'mars_base_internal_temperature'
EX_TEMP = 'mars_base_external_temperature'
HUMIDITY = 'mars_base_internal_humidity'
ILLUMINANCE = 'mars_base_external_illuminance'
CO2 = 'mars_base_internal_co2'
OXYGEN = 'mars_base_internal_oxygen'

# 환경값에 대한 로그를 생성할 파일의 경로.
LOG_PATH= 'mission004/mars_env_values.log'


# 더미 환경 센서 클래스.
class DummySensor:
    # DummySensor 클래스 초기화.
    def __init__(self):
        # 화성 기지의 내부, 외부의 온도, 습도, 광량, 이산화탄소 농도, 산소 농도 초기화.
        self._env_values = {}
        # 화성 기지의 환경 값의 더미 데이터 생성을 위한 범위 값 지정.
        self._env_ranges = {
            IN_TEMP: (18, 30),
            EX_TEMP: (0, 21),
            HUMIDITY: (50, 60),
            ILLUMINANCE: (500, 715),
            CO2: (0.02, 0.1),
            OXYGEN: (4, 7)
        }
    
    # 각 변수에 환경값을 설정.
    def set_env(self, env_values):
        self._env_values = env_values
        for key, value_range in self._env_ranges.items():
            self._env_values[key] = random.uniform(*value_range)

    # 랜덤 값으로 설정된 변수를 반환.
    def get_env(self):
        return self._env_values