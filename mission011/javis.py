import os # 파일 시스템 작업을 위한 내장 라이브러리.
import sounddevice # 음성 녹음을 위한 외부 라이브러리.
import speech_recognition as sr # STT 외부 라이브러리.
from datetime import datetime # 날짜, 시간 처리를 위한 내장 라이브라리.
from scipy.io.wavfile import write # 파일 저장을 위한 외부 라이브러리.
from pydub import AudioSegment # 음성 파일 처리를 위한 외부 라이브러리.

# 음성 파일 경로. (이제 기본값 또는 사용자 지정 경로로 사용됨)
RECORD_PATH = 'mission011/records' 
# STT 변환 텍스트 파일(CSV) 경로.
CSV_PATH = 'mission011/statements'

# 음성 녹음을 진행하고, WAV 파일로 저장하는 클래스.
class Javis:
    # 수정: __init__ 메서드에 record_path 매개변수 추가
    def __init__(self, record_path: str = RECORD_PATH):
        self._samplerate: int = 44100 # 샘플링 횟수(Hz 단위(기본값: 44,100))
        self.record_path = record_path # 사용자가 지정한 녹음 경로 저장

    # 기본 오디오 장치 중 입력 장치의 상태를 확인하는 함수.
    def _check_microphone_status(self):
        '''
        Args:
            None
        Returns:
            bool: 마이크의 연결 상태를 확인하고 사용 가능 여부 판단.
        '''
        print('INFO: 마이크 연결 상태를 확인합니다...')
        try:
            default_input_devices = sounddevice.default.device[0]
            input_devices = sounddevice.query_devices()
            
            if not input_devices or default_input_devices is None:
                print('WARNING: 오디오 장치를 찾을 수 없거나 기본 입력 장치가 설정되어 있지 않습니다.')
                return False
            
            info_input_devices = input_devices[default_input_devices]

            if info_input_devices['max_input_channels'] > 0:
                print(f'INFO: 마이크가 정상적으로 연결되어 있습니다: {info_input_devices['name']}')
                return True
            else:
                print(f'ERROR: 기본 입력 장치 "{info_input_devices}"는 입력 기능을 지원하지 않습니다.')
                return False
        except Exception as error:
            print(f'ERROR: 알 수 없는 오류가 발생했습니다: {error}')

    # 마이크를 통해 음성을 녹음하는 함수.
    def record_audio(self, duration):
        '''
        Args:
            duration (int): 녹음 시간 (초 단위)
        Returns:
            audio_data (numpy.ndarray): 녹음된 음성 데이터.
        '''
        print(f'INFO: {duration}초 동안 음성 녹음을 진행합니다...')
        audio_data = sounddevice.rec(
            frames=int(duration * self._samplerate),
            samplerate=self._samplerate,
            channels=2,
            dtype='int16'
        )
        sounddevice.wait()
        print(f'INFO: {duration}초 동안 녹음을 완료했습니다...')
        return audio_data

    # 녹음된 음성 데이터를 WAV 파일로 저장하는 함수.
    def saved_audio(self, audio_data):
        '''
        Args:
            audio_data (numpy.ndarray): 녹음된 음성 데이터의 NumPy 배열.
        Returns:
            str: 저장된 오디오 파일의 전체 경로.
        '''
        audio_name = f'{datetime.now().strftime('%Y%m%d-%H%M%S')}.wav'
        # 수정: self.record_path 사용
        full_audio_path = os.path.join(self.record_path, audio_name) 
        write(
            filename=full_audio_path,
            rate=self._samplerate,
            data=audio_data
        )
        print(f'INFO: 음성 데이터를 {audio_name}(으)로 저장되었습니다.')
        return full_audio_path

    # 저장된 녹음 파일의 목록을 출력하는 함수.
    def list_audio_files(self, start_date_string, end_date_string):
        '''
        Args:
            start_date_string (str): 검색할 범위의 시작일 (YYYYMMDD 형식)
            end_date_string (str): 검색할 범위의 종료일 (YYYYMMDD 형식)
        Returns:
            list: 조건을 만족하는 오디오 파일의 전체 경로 목록.
        '''
        found_audio_files = []
        # 수정: self.record_path 사용
        if not os.path.exists(self.record_path):
            print(f'WARNING: 지정된 녹음 경로가 존재하지 않습니다: {self.record_path}')
            return []

        for filename in os.listdir(self.record_path): # 수정: self.record_path 사용
            if filename.lower().endswith('.wav'):
                try:
                    file_date_time_string = filename.rsplit('.', 1)[0]
                    file_date_string = file_date_time_string.split('-')[0]
                    
                    file_date = datetime.strptime(file_date_string, '%Y%m%d').date()
                    
                    if start_date_string:
                        start_date = datetime.strptime(start_date_string, '%Y%m%d').date()
                        if file_date < start_date:
                            continue
                    if end_date_string:
                        end_date = datetime.strptime(end_date_string, '%Y%m%d').date()
                        if file_date > end_date:
                            continue
                    
                    # 수정: self.record_path 사용
                    found_audio_files.append(os.path.join(self.record_path, filename))
                except ValueError:
                    print(f'WARNING: 유효한 날짜 형식의 WAV 파일이 아닙니다: {filename}')
                    continue
                except Exception as error:
                    print(f'ERROR: 파일 처리 중 알 수 없는 오류가 발생했습니다: {error}')
            
        if found_audio_files:
            print('\n--- 검색된 음성 파일 목록 ---')
            for filepath in found_audio_files:
                print(os.path.basename(filepath))
            return found_audio_files
        else:
            print('WARNING: 지정 범위에 해당하는 음성 파일이 존재하지 않습니다.')
            return []

    # 음성 파일을 텍스트로 변환하고 CSV로 저장하는 함수.
    def convert_audio_to_text_and_save_csv(self, audio_file_path):
        '''
        Args:
            audio_file_path (str): 변환할 음성 파일의 전체 경로.
        Returns:
            None
        '''
        recognizer = sr.Recognizer()
        
        # WAV 형식이 아니면 WAV로 변환 (pydub 사용)
        if not audio_file_path.lower().endswith('.wav'):
            print(f'WARNING: {os.path.basename(audio_file_path)} 파일은 WAV 형식이 아닙니다. 변환을 시도합니다.')
            try:
                audio = AudioSegment.from_file(audio_file_path)
                wav_file_path = audio_file_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_file_path, format='wav')
                audio_file_path = wav_file_path
                print(f'INFO: {os.path.basename(audio_file_path)} (으)로 변환되었습니다.')
            except Exception as e:
                print(f'ERROR: WAV 파일 변환 중 오류가 발생했습니다: {e}')
                return

        with sr.AudioFile(audio_file_path) as source:
            print(f'INFO: {os.path.basename(audio_file_path)} 파일에서 텍스트를 추출 중입니다...')
            try:
                audio_data = recognizer.record(source) # 전체 오디오 파일 읽기
                text = recognizer.recognize_google(audio_data, language='ko-KR') # 한국어 설정
                print(f'INFO: 인식된 텍스트: "{text}"')
                
                # 고정된 CSV 파일 이름 설정
                fixed_csv_file_name = 'stt_to_csv.csv'
                full_csv_path = os.path.join(CSV_PATH, fixed_csv_file_name)
                
                # CSV_PATH 디렉토리가 없으면 생성
                if not os.path.exists(CSV_PATH):
                    os.makedirs(CSV_PATH)

                # 파일이 이미 존재하는지 확인 (헤더 추가 여부 판단용)
                file_exists = os.path.exists(full_csv_path)
                
                # 음성 파일 이름 추출.
                audio_file_name = os.path.splitext(os.path.basename(audio_file_path))[0]
                # 음성 파일 이름을 timestamp로 형식 변환.
                try:
                    # 음성 파일 이름을 datetime 객체로 파싱.
                    date_obj = datetime.strptime(audio_file_name, '%Y%m%d-%H%M%S')
                    # 추출한 날짜와 시간을 timestamp로 형식 변환.
                    timestamp = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    
                except ValueError:
                    # 형식이 맞지 않는 경우, 원본 파일 이름을 그대로 사용
                    timestamp = audio_file_name
                    print(f"WARNING: '{audio_file_name}'는 예상한 날짜/시간 형식이 아닙니다. 원본 파일 이름을 그대로 사용합니다.")
                
                # 파일을 'a'(추가) 모드로 열고, 파일이 없었다면 헤더를 작성
                with open(full_csv_path, 'a', encoding='utf-8-sig') as f:
                    if not file_exists: # 파일이 새로 생성되는 경우에만 헤더 작성
                        f.write('Timestamp,SpeechToText\n') # 헤더 변경
                    
                    # 새로운 내용 추가: AudioFileName,Recognized Text 형식
                    f.write(f'"{timestamp}","{text}"\n') # 따옴표로 각 필드 감싸기
                
                print(f'INFO: 텍스트가 {fixed_csv_file_name}(으)로 추가되었습니다.')
            except sr.UnknownValueError:
                print('WARNING: 음성을 인식할 수 없습니다.')
            except sr.RequestError as e:
                print(f'ERROR: Google Web Speech API에 연결할 수 없습니다; {e}')
            except Exception as e:
                print(f'ERROR: 텍스트 변환 중 알 수 없는 오류가 발생했습니다: {e}')
    
    # CSV 파일에서 키워드를 검색하는 함수.
    def search_text_in_csv_files(self, keyword):
        '''
        Args:
            keyword (str): 검색할 키워드.
        Returns:
            None
        '''
        print(f'\n--- "{keyword}" 키워드 검색 결과 ---')
        found_matches = False
        if not os.path.exists(CSV_PATH):
            print('INFO: 텍스트 파일이 저장된 디렉토리가 없습니다.')
            return
            
        for filename in os.listdir(CSV_PATH):
            if filename.lower().endswith('.csv'):
                full_csv_path = os.path.join(CSV_PATH, filename)
                try:
                    with open(full_csv_path, 'r', encoding='utf-8-sig4') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if i == 0:
                                continue
                            parts = line.strip().split(',', 1)
                            if len(parts) > 1:
                                recognized_text = parts[1].strip().strip('"')
                                if keyword.lower() in recognized_text.lower():
                                    print(f'파일: {filename}, 시간: {parts[0]}, 내용: "{recognized_text}"')
                                    found_matches = True
                except FileNotFoundError:
                    print(f'WARNING: 파일을 찾을 수 없습니다: {filename}')
                except Exception as e:
                    print(f'ERROR: {filename} 파일 읽기 중 오류가 발생했습니다: {e}')

        if not found_matches:
            print(f'INFO: "{keyword}"(을)를 포함하는 텍스트를 찾을 수 없습니다.')

    # 추가: 녹음 경로를 설정하는 함수
    def set_record_path(self, new_path: str):
        '''
        Args:
            new_path (str): 새로 설정할 녹음 파일 경로.
        Returns:
            bool: 경로 설정 성공 여부.
        '''
        if os.path.isdir(new_path):
            self.record_path = new_path
            print(f'INFO: 녹음 파일 경로가 다음으로 설정되었습니다: {self.record_path}')
            return True
        else:
            print(f'ERROR: 유효하지 않은 경로입니다. 디렉토리가 존재하지 않거나 접근할 수 없습니다: {new_path}')
            return False
            
# 코드 실행.
if __name__ == '__main__':
    # Javis 클래스 인스턴스 생성. (초기에는 기본 경로 사용)
    javis = Javis() 
    
    while True:
        print('-'*30)
        print(f'현재 녹음/조회 경로: {javis.record_path}') # 현재 경로 표시
        print('1 입력: 녹음/조회 경로 설정.') # 추가
        print('2 입력: 음성 녹음 및 텍스트 변환.')
        print('3 입력: 날짜별 음성 파일 조회.')
        print('4 입력: 기존 음성 파일 텍스트 변환.')
        print('5 입력: 키워드 검색.')
        print('6 입력: 코드 종료.')
        choice = input('1~6값을 입력하시오: ') # 메뉴 번호 변경
        
        # CSV_PATH 디렉토리 존재 여부 확인 및 생성 (RECORD_PATH는 이제 사용자가 설정함)
        if not os.path.exists(CSV_PATH):
            os.makedirs(CSV_PATH)
        
        # 1. 녹음/조회 경로 설정.
        if choice == '1':
            new_record_dir = input('새로운 녹음/조회 경로를 입력하시오: ')
            # 사용자가 입력한 경로가 비어있으면 기본 경로로 설정 (선택 사항)
            if not new_record_dir:
                javis.set_record_path(RECORD_PATH)
            else:
                javis.set_record_path(new_record_dir)
            # 경로 설정 후 해당 디렉토리가 없으면 생성 시도
            if not os.path.exists(javis.record_path):
                try:
                    os.makedirs(javis.record_path)
                    print(f'INFO: 지정된 녹음 경로 {javis.record_path}가 생성되었습니다.')
                except Exception as e:
                    print(f'ERROR: 녹음 경로 {javis.record_path}를 생성할 수 없습니다: {e}')

        # 2. 음성 녹음 및 텍스트 변환. (메뉴 번호 변경)
        elif choice == '2':
            # 변경된 record_path가 유효한지 확인
            if not os.path.exists(javis.record_path):
                print(f'ERROR: 녹음 경로 "{javis.record_path}"가 유효하지 않습니다. 먼저 경로를 설정하거나 유효한 경로를 지정하십시오.')
                continue # 다음 루프
            
            if javis._check_microphone_status():
                try:
                    record_duration = int(input('녹음 시간을 입력하시오(기본값: 10초): ') or '10')
                    recorded_data = javis.record_audio(duration=record_duration)
                    saved_audio_path = javis.saved_audio(audio_data=recorded_data)
                    
                    if saved_audio_path:
                        javis.convert_audio_to_text_and_save_csv(audio_file_path=saved_audio_path)
                except ValueError:
                    print('ERROR: 유효한 녹음 시간을 입력하십시오.')
                except Exception as error:
                    print(f'ERROR: 알 수 없는 오류가 발생했습니다: {error}')
        # 3. 날짜별 음성 파일 조회. (메뉴 번호 변경)
        elif choice == '3':
            # 변경된 record_path가 유효한지 확인
            if not os.path.exists(javis.record_path):
                print(f'ERROR: 조회 경로 "{javis.record_path}"가 유효하지 않습니다. 먼저 경로를 설정하거나 유효한 경로를 지정하십시오.')
                continue
            
            print('입력한 시작일, 종료일 범위의 파일 목록을 출력합니다.')
            print('날짜 조회 시YYYYMMDD 형식으로 입력하시오.')
            print('시작일, 종료일을 공백으로 입력하면 전체 목록 출력.')
            start_date = input('시작일: ')
            end_date = input('종료일: ')
            javis.list_audio_files(
                start_date_string=start_date,
                end_date_string=end_date
            )
        # 4. 기존 음성 파일 텍스트 변환. (메뉴 번호 변경)
        elif choice == '4':
            # 변경된 record_path가 유효한지 확인
            if not os.path.exists(javis.record_path):
                print(f'ERROR: 변환할 음성 파일 경로 "{javis.record_path}"가 유효하지 않습니다. 먼저 경로를 설정하거나 유효한 경로를 지정하십시오.')
                continue
                
            print('\n--- 텍스트로 변환할 음성 파일을 선택합니다 ---')
            available_audio_files = javis.list_audio_files(start_date_string='', end_date_string='')
            
            if available_audio_files:
                print('\n변환할 파일의 번호를 입력하거나, 전체 변환하려면 "all"을 입력하세요.')
                for i, filepath in enumerate(available_audio_files):
                    print(f'{i+1}. {os.path.basename(filepath)}')
                
                choice_file = input('선택: ')
                
                if choice_file.lower() == 'all':
                    for filepath in available_audio_files:
                        javis.convert_audio_to_text_and_save_csv(filepath)
                else:
                    try:
                        index = int(choice_file) - 1
                        if 0 <= index < len(available_audio_files):
                            javis.convert_audio_to_text_and_save_csv(available_audio_files[index])
                        else:
                            print('WARNING: 유효하지 않은 번호입니다.')
                    except ValueError:
                        print('WARNING: 유효하지 않은 입력입니다.')
            else:
                print('INFO: 변환할 음성 파일이 없습니다.')
        # 5. 키워드 검색. (메뉴 번호 변경)
        elif choice == '5':
            print('입력한 키워드를 CSV 파일 내에서 검색하여 출력합니다.')
            input_keyword = input('검색할 키워드 입력: ')
            javis.search_text_in_csv_files(input_keyword)
        # 6. 코드 종료. (메뉴 번호 변경)
        elif choice == '6':
            print('INFO: JAVIS를 종료합니다.')
            break
        # 유효하지 않은 값 입력 시 경고 메시지 출력.
        else:
            print('WARNING: 유효하지 않은 선택입니다. 다시 입력하십시오.')