# log 파일 읽기.
try:
    with open('mission001/mission_computer_main.log', 'r', encoding='utf-8') as log_file:
        # 효율적인 메모리 사용을 위해 readlines() 사용.
        log_lines = log_file.readlines()
        for line in log_lines:
            print(line.strip())
# 해당 경로에 파일이 존재하지 않을 경우,
except FileNotFoundError:
    print('ERROR: 파일이 존재하지 않습니다.')
# 파일에 접근할 권한이 없을 경우,
except PermissionError:
    print('ERROR: 파일에 대한 권한이 없습니다.')
# 예기치 못한 오류가 발생할 경우,
except Exception as error:
    print('ERROR: 파일 읽는 중 오류 발생: ', error)

# 사고 원인 보고서 작성.
try:
    with open('mission001/log_analysis.md', 'w', encoding='utf-8') as error_report:
        data = '성공적으로 도착했으나 산소 탱크가 폭발해 센터와 제어 시스템이 꺼졌다.'
        error_report.write(data)
        print('원인 보고서가 생성되었습니다.')
# 파일 생성 시 동일한 이름의 파일이 존재할 경우,
except FileExistsError:
    print('ERROR: 파일을 생성할 수 없습니다.')
# 예기치 못한 오류가 발생할 경우,
except Exception as error:
    print('ERROR: 보고서 생성 중 오류 발생: ', error)