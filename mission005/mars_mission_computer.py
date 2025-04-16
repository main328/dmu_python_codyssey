import platform
import psutil

# 설정 파일의 경로.
FILE_PATH = 'mission005/setting.txt'

class MissionComputer:
    def __init__(self, file_path):
        self._path = file_path
        self._source = {
            'system_info': {
                'OS': lambda: platform.system(),
                'OS Version': lambda: platform.version(),
                'CPU Type': lambda: platform.processor(),
                'CPU Core': lambda: psutil.cpu_count(logical=True),
                'Memory': lambda: int(round(psutil.virtual_memory().total / (1024 ** 3), 0))
            },
            'usage_info': {
                'CPU usage': lambda: psutil.cpu_percent(interval=1),
                'Memory usage': lambda: psutil.virtual_memory().percent
            }
        }

        self._settings = self._load_settings()

    def _load_settings(self):
        settings = {section: {} for section in self._source}
        current_section = None

        try:
            with open(self._path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                        if section in settings:
                            current_section = section
                        continue

                    if '=' in line and current_section:
                        key, value = map(str.strip, line.split('=', 1))
                        settings[current_section][key] = value.lower() == 'true'
        except FileNotFoundError:
            print("설정 파일을 찾을 수 없습니다. 기본값을 모두 True로 설정합니다.")
            for section, items in self._source.items():
                settings[section] = {key: True for key in items}

        return settings

    def _extract_info_by_section(self, section_name):
        result = {}
        for key, func in self._source[section_name].items():
            if self._settings[section_name].get(key, False):
                try:
                    result[key] = func()
                except Exception as error:
                    result[key] = 'Unknown'
                    print(f"[ERROR] {key} 항목 추출 실패: {error}")
        return result

    def get_mission_computer_info(self):
        return self._extract_info_by_section('system_info')

    def get_mission_computer_load(self):
        return self._extract_info_by_section('usage_info')

    def format_as_json(self, data, indent=4):
        json_str = "{\n"
        for i, (key, value) in enumerate(data.items()):
            # 문자열은 큰따옴표로 감싸고, 숫자는 그대로 표시
            value_str = f'"{value}"' if isinstance(value, str) else value
            comma = ',' if i < len(data) - 1 else ''
            json_str += " " * indent + f'"{key}": {value_str}{comma}\n'
        json_str += "}"
        return json_str

if __name__ == '__main__':
    run_computer = MissionComputer(FILE_PATH)
    info = run_computer.get_mission_computer_info()
    load = run_computer.get_mission_computer_load()

    print("=== System Info ===")
    print(run_computer.format_as_json(info))

    print("\n=== Usage Info ===")
    print(run_computer.format_as_json(load))
