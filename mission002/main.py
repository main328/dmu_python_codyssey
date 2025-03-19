# 파일이 위치한 경로.
CSV_PATH = 'mission002/Mars_Base_Inventory_List.csv'
FLAME_PATH = 'mission002/Mars_Base_Inventory_danger.csv'
BIN_PATH = 'mission002/Mars_Base_Inventory_List.bin'

# csv 파일을 읽고 List 객체로 변환하는 함수.
def read_csv(path):
    # 목록을 저장할 List 객체 생성.
    csv_data = []
    # csv 파일을 읽을 때 발생할 수 있는 예외 처리.
    try:
        # with는 오류가 발생해도 자동으로 close()를 호출.
        with open(path, 'r', encoding='utf-8') as inventory:
            # 효율적인 메모리 사용을 위해 while문과 readline() 사용.
            while True:
                line = inventory.readline()
                if not line:
                    break
                # 라인이 존재하면 순차적으로 List 객체에 저장.
                csv_data.append(line.strip())
    # 해당 경로에 파일이 존재하지 않을 경우,
    except FileNotFoundError:
        print('ERROR: 파일을 찾을 수 없습니다.')
    # 파일에 대한 접근 권한이 없을 경우,
    except PermissionError:
        print('ERROR: 파일의 접근 권한이 없습니다.')
    # 파일을 인코딩할 수 없을 경우,
    except UnicodeEncodeError:
        print('파일을 읽을 수 없습니다.')
    # 알 수 없는 오류가 발생할 경우,
    except Exception as error:
        print('ERROR: 알 수 없는 오류가 발생: ', error)
    
    return csv_data

# 인화성이 높은 순으로 정렬하고 0.7 이상만 추리는 함수.
def sort_csv(flammable):
    # 인화성 수치가 0.7 이상인 List 객체 생성.
    csv_sort = []
    
    # 반복문을 사용해 목록의 인화성 수치 비교.
    for line in flammable:
        try:
            flammability = float(line.split(',')[4])
            # 인화성 수치가 0.7 이상인 라인만 추가.
            if flammability >= 0.7:
                csv_sort.append(line)
        # 숫자를 변환할 수 없는 행일 경우 무시.
        except ValueError:
            continue
    
    return csv_sort

# 정렬된 목록을 csv 파일로 저장하는 함수.
def save_csv(path, header, inventory):
    try:
        with open(path, 'w', encoding='utf-8') as save:
            # 헤더 영역 저장.
            save.write(header + '\n')
            # 반복문을 사용해서 목록 저장.
            for line in inventory:
                save.write(line + '\n')
            print('-----고인화성 물질 목록을 저장했습니다.-----')
    # 지정한 경로를 찾을 수 없을 경우,
    except FileNotFoundError:
        print('ERROR: 지정한 경로를 찾을 수 없습니다.')
    # 파일 쓰기 권한이 없는 겅우,
    except PermissionError:
        print('ERROR: 파일을 저장할 권한이 없습니다.')
    # 알 수 없는 오류가 발생할 경우,
    except Exception as error:
        print('ERROR: 알 수 없는 오류 발생: ', error)

# bin 파일을 읽고 list로 변환하는 함수.
def read_bin(path):
    # 목록을 저장한 list 객체 생성.
    bin_data = []

    # bin 파일을 읽을 때 발생할 수 있는 예외 처리.
    try:
        # with는 오류가 발생해도 자동으로 close()를 호출.
        with open(path, 'rb') as inventory:
            # 효율적인 메모리 사용을 위해 while문과 readline() 사용.
            while True:
                line = inventory.readline()
                if not line:
                    break
                # 라인이 존재하면 순차적으로 List 객체에 저장.
                bin_data.append(line.decode('utf-8').strip())
    # 해당 경로에 파일이 존재하지 않을 경우,
    except FileNotFoundError:
        print('ERROR: 파일을 찾을 수 없습니다.')
    # 파일에 대한 접근 권한이 없을 경우,
    except PermissionError:
        print('ERROR: 파일의 접근 권한이 없습니다.')
    # 알 수 없는 오류가 발생할 경우,
    except Exception as error:
        print('ERROR: 알 수 없는 오류가 발생: ', error)
    
    return bin_data

# 정렬된 목록을 bin 파일로 저장하는 함수.
def save_bin(path, header, inventory):
    try:
        with open(path, 'wb') as save:
            # 헤더 영역 저장.
            save.write((header + '\n').encode('utf-8'))
            # 데이터 영역 저장.
            for line in inventory:
                save.write((line + '\n').encode('utf-8'))
    # 지정한 경로를 찾을 수 없을 경우,
    except FileNotFoundError:
        print('ERROR: 지정한 경로를 찾을 수 없습니다.')
    # 파일 쓰기 권한이 없는 겅우,
    except PermissionError:
        print('ERROR: 파일을 저장할 권한이 없습니다.')
    # 알 수 없는 오류가 발생할 경우,
    except Exception as error:
        print('ERROR: 알 수 없는 오류 발생: ', error)

# 실행 코드.
try:
    # 적재화물 목록 출력.
    inventory_csv = read_csv(CSV_PATH)
    print('-----적재화물 목록 전체 출력-----')
    for line in inventory_csv:
        print(line.strip())
    
    # csv 파일의 헤더 영역과 데이터 영역 분리.
    header = inventory_csv[0]
    body = inventory_csv[1:]
    # sorted()와 람다식을 사용해 인화성을 기준으로 정렬.
    flammable = sorted(body, key=lambda x: float(x.split(',')[4]), reverse=True)

    # 인화성이 높은 순으로 정렬하고 0.7 이상만 출력.
    print('-----고인화성성 물질 목록----')
    print(header)
    flame = sort_csv(flammable)
    for line in flame:
        print(line.strip())
    
    # 인화성 수치로 분류한 List를 csv 파일로 저장.
    save_csv(FLAME_PATH, header,flame)

    # 인화성 높은 순으로 정렬된 목록을 bin 파일로 저장.
    save_bin(BIN_PATH, header, flammable)

    # bin 파일 출력.
    inventory_bin = read_bin(BIN_PATH)
    print('-----bin 파일의 목록 출력-----')
    for line in inventory_bin:
        print(line)
# 알 수 없는 오류가 발생할 경우,
except Exception as error:
    print('ERROR: 알 수 없는 오류가 발생: ', error)