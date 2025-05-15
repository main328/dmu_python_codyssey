import zipfile
import threading
import logging
import time
import io
import copy

# 설정
charset = [chr(c) for c in range(ord('a'), ord('z') + 1)] + [str(d) for d in range(10)]
password_length = 6
zip_path = "mission008/file/emergency_storage_key.zip"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("mission008/zip_cracker.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 중복 제한 검사
def is_within_max_dup(password, max_dup):
    return all(password.count(c) <= max_dup for c in set(password))

# 비밀번호 생성기
def generate_passwords_with_prefix(prefix, charset, length):
    if length == 0:
        yield prefix
    else:
        for char in charset:
            yield from generate_passwords_with_prefix(prefix + char, charset, length - 1)

# 공유 flag
found_event = threading.Event()
found_password = None
lock = threading.Lock()

# 스레드 작업
def crack_zip_thread(thread_id, zip_bytes_copy, fixed_char, max_dup):
    global found_password

    zip_stream = io.BytesIO(zip_bytes_copy)
    try:
        zip_file = zipfile.ZipFile(zip_stream)
    except Exception as e:
        logging.error(f"[Thread-{thread_id}] ZIP 파일 읽기 실패: {e}")
        return

    logging.info(f"[Thread-{thread_id}] 시작 문자 '{fixed_char}', 최대 중복 {max_dup} 허용")

    for password in generate_passwords_with_prefix(fixed_char, charset, password_length - 1):
        if found_event.is_set():
            return
        if not is_within_max_dup(password, max_dup):
            continue

        logging.info(f"[Thread-{thread_id}] [시도] 비밀번호: {password}")
        try:
            zip_file.extractall(pwd=password.encode('utf-8'))
            with lock:
                if not found_event.is_set():
                    found_password = password
                    found_event.set()
                    logging.info(f"[Thread-{thread_id}] [성공] 비밀번호: {password}")
            return
        except:
            continue

# 단계별 실행
def crack_zip_with_phases(zip_path):
    global found_password
    start_time = time.time()

    # ZIP 파일을 한 번 메모리에 로드
    with open(zip_path, 'rb') as f:
        original_zip_bytes = f.read()

    for phase in range(1, 7):
        logging.info(f"\n[단계 {phase}] 최대 {phase}개 중복 허용 시작...\n")
        threads = []

        for idx, fixed_char in enumerate(charset):
            zip_bytes_copy = copy.deepcopy(original_zip_bytes)
            t = threading.Thread(target=crack_zip_thread, args=(idx, zip_bytes_copy, fixed_char, phase))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if found_event.is_set():
            break

    end_time = time.time()

    if found_password:
        logging.info(f"\n[완료] 비밀번호: {found_password}")
    else:
        logging.warning("[실패] 비밀번호를 찾지 못했습니다.")

    logging.info(f"[소요 시간] 총 {end_time - start_time:.2f}초")

# 실행
if __name__ == "__main__":
    crack_zip_with_phases(zip_path)
