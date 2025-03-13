# 출력 결과를 시간의 역순으로 정렬해 출력.
try:
    with open('codyssey001/mission_computer_main.log', 'r', encoding='utf-8') as log_file:
        log_lines = log_file.readlines()
        header_line = log_lines[0]
        body_line = log_lines[1:]
        body_line_rev = sorted(body_line, key=lambda x: x.split(",")[0], reverse=True)
        
        print(header_line.strip())
        for body in body_line_rev:
            print(body.strip())
# 해당 경로에 파일이 존재하지 않을 경우,
except FileNotFoundError:
    print('ERROR: 파일이 존재하지 않습니다.')
# 파일에 접근할 권한이 없을 경우,
except PermissionError:
    print('ERROR: 파일에 대한 권한이 없습니다.')
# 예기치 못한 오류가 발생할 경우,
except Exception as error:
    print('ERROR: 파일 읽는 중 오류 발생: ', error)

#출력 결과 중 문제가 되는 부분만 따로 파일로 저장.
try:
    with open('codyssey001/bonus_error_line.log', 'w', encoding='utf-8') as error_log_file:
        error_log_file.write(header_line)
        error_log_file.write(body_line_rev[0])
        error_log_file.write(body_line_rev[1])
        error_log_file.write(body_line_rev[2])
        print('사고 원인 로그 분류해 저장했습니다.')
# 파일 생성 시 동일한 이름의 파일이 존재할 경우,
except FileExistsError:
    print('ERROR: 파일을 생성할 수 없습니다.')
# 예기치 못한 오류가 발생할 경우,
except Exception as error:
    print('ERROR: 보고서 생성 중 오류 발생: ', error)