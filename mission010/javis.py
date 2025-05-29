import os # 파일 시스템 작업을 위한 내장 라이브러리.
import sounddevice # 음성 녹음을 위한 외부 라이브러리.
from datetime import datetime # 날짜, 시간 처리를 위한 내장 라이브라리.
from scipy.io.wavfile import write # 파일 저장을 위한 외부 라이브러리.

# 음성 파일 경로.
RECORD_PATH = 'mission010/records'

# 음성 녹음을 진행하고, WAV 파일로 저장하는 클래스.
class Javis:
    def __init__(self):
        # 내부적으로 사용되는 변수는 언더스코어(_)로 생성.
        self._samplerate: int = 44100 # 샘플링 횟수(Hz 단위(기본값: 44,100))
            
    # 마이크를 통해 음성을 녹음하는 함수.
    def record_audio(self, duration):
        '''
        Arguments:
            duration (int): 녹음 시간 (초 단위)
        return:
            audio_data (numpy.ndarray): 녹음된 음성 데이터.
        '''
        print(f'{duration}초 동안 음성 녹음을 진행합니다...')
        # sounddevice.rec 함수는 음성을 녹음하고 NumPy 배열로 반환.
        audio_data = sounddevice.rec(
            frames=int(duration*self._samplerate), # 녹음할 음성 프레임 총 개수.
            samplerate=self._samplerate, # 샘플링 횟수(Hz 단위(기본값: 44,100))
            channels=2, # 음성 채널 수.
            dtype='int16' # 음성 데이터를 저장할 데이터 타입.
        )
        # 녹음이 완료될 때까지 대기.
        sounddevice.wait()
        print(f'{duration}초 동안 녹음을 완료했습니다...')
        # 녹음된 음성 데이터의 NumPy 배열 반환.
        return audio_data

    # 녹음된 음성 데이터를 WAV 파일로 저장하는 함수.
    def saved_audio(self, audio_data):
        '''
        Arguments:
            audio_data (numpy/ndarray): 녹음된 음성 데이터의 NumPy 배열.
        '''
        # 음성 파일 이름 생성.2
        
        audio_name = f'{datetime.now().strftime('%Y%m%d-%H%M%S')}.wav'
        # write 함수를 사용하여 WAV 파일로 저장.
        write(
            filename=f'{RECORD_PATH}/{audio_name}', # 저장할 음성 파일의 이름.
            rate=self._samplerate, # 샘플링 횟수(Hz 단위(기본값: 44,100))
            data=audio_data # 저장할 음성 데이터.
        )
        print(f'음성 데이터를 {audio_name}(으)로 저장되었습니다.')
    
    # 저장된 녹음 파일의 목록을 출력하는 함수.
    def list_audio_files(self, start_date_string, end_date_string):
        '''
        Arguments:
            start_date_string (str): 검색할 범위의 시작일 (YYYYMMDD 형식)
            end_date_string (str): 검색할 범위의 종료일 (YYYYMMDD 형식)
        '''
        # 범위에 따른 파일 이름을 저장하는 리스트.
        found_audio_files = []
        # records 폴더 내 파일 순회.
        for filename in os.listdir(RECORD_PATH):
            # wav 파일만 목록으로 추출.
            if filename.endswith('.wav'):
                # 예외 처리 진행.
                try:
                    # 파일 이름에서 날짜 추출.
                    file_date_string = filename.split('_')[0]
                    # 추출한 날짜를 datetime 객체로 변환.
                    file_date = datetime.strptime(file_date_string, '%Y%m%d').date()
                    
                    # 시작일이 존재할 경우,
                    if start_date_string:
                        start_date = datetime.strptime(start_date_string, '%Y%m%d').date()
                        # 시작일 이전 파일 제외.
                        if file_date < start_date:
                            continue
                    # 종료일이 존재할 경우,
                    if end_date_string:
                        end_date = datetime.strptime(end_date_string, '%Y%m%d').date()
                        # 종료일 이후 파일 제외.
                        if file_date > end_date:
                            continue
                    # 조건을 만족하는 filename을 found_audio_files 리스트에 추가.
                    found_audio_files.append(filename)
                except ValueError:
                    print(f'WAV 파일이 아닙니다: {filename}')
                    continue
                except Exception as error:
                    print(f'알 수 없는 오류가 발생했습니다: {error}')
            
        # 검색된 파일이 존재할 경우,
        if found_audio_files:
            # 파일 목록 출력.
            for filename in found_audio_files:
                print(filename)
        # 검색된 파일이 존재하지 않을 경우,
        else:
            # 경고 메시지 출력.
            print('지정 범위에 해당하는 음성 파일이 존재하지 않습니다.')
    
# 코드 실행.
if __name__ == '__main__':
    # Javis 클래스 인스턴스 생성.
    javis = Javis()
    while True:
        #선택지 출력.
        print('-'*30)
        print('1 입력: 음성 녹음.')
        print('2 입력: 날짜 조회.')
        print('3 입력: 코드 종료.')
        choice = input('1~3값을 입력하시오: ')
        
        # records 디렉토리 존재 여부 확인.
        if not os.path.exists(RECORD_PATH):
            os.makedirs(RECORD_PATH)
        
        # 1. 음성 녹음.
        if choice == '1':
            # 예외 처리 진행.
            try:
                # 음성 녹음 시간 입력.
                record_duration = int(input('녹음 시간을 입력하시오: ') or '10')
                # 음성 녹음 함수 실행.
                recorded_data = javis.record_audio(duration=record_duration)
                # 음성 저장 함수 실행.
                javis.saved_audio(audio_data=recorded_data)
            except Exception as error:
                print(f'알 수 없는 오류가 발생했습니다: {error}')
        # 2. 날짜 조회.
        elif choice == '2':
            print('입력한 시작일, 종료일 범위의 파일 목록을 출력합니다.')
            print('날짜 조회 시 YYYYMMDD 형식으로 입력하시오.')
            print('시작일, 종료일을 공백으로 입력하면 전체 목록 출력.')
            start_date = input('시작일: ')
            end_date = input('종료일: ')
            # 입력한 범위에 해당하는 파일 목록 출력.
            javis.list_audio_files(
                start_date_string=start_date,
                end_date_string=end_date
            )
        # 3. 코드 종료.
        elif choice == '3':
            print('JAVIS를 종료합니다.')
            break
        # 1~3을 제외한 값을 입력하면 경고 메시지 출력.
        else:
            print('유효하지 않은 선택입니다. 다시 입력하십시오.')