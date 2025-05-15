import zipfile
import multiprocessing
import time
import ctypes
import io
from itertools import permutations

zip_path = 'mission008/file/emergency_storage_key.zip'
PASSWORD_LENGTH = 6
CHARSET = "etaoinshrdlucmfwypvbgkqjxz0123456789"
NUM_PROCESSES = multiprocessing.cpu_count()

found_event = multiprocessing.Event()
found_password = multiprocessing.Array(ctypes.c_char, PASSWORD_LENGTH + 1, lock=multiprocessing.Lock())
start_time = 0
end_time = 0

def crack_process(process_id, password_queue, zip_memory_data):
    try:
        zip_memory = io.BytesIO(zip_memory_data)
        while not found_event.is_set():
            try:
                password_tuple = password_queue.get(timeout=0.1)
                password = "".join(password_tuple)
                with zipfile.ZipFile(zip_memory) as zip_file:
                    try:
                        zip_file.extractall(pwd=password.encode())
                        if not found_event.is_set():
                            with found_password.get_lock():
                                if not found_password[:] and not found_event.is_set():
                                    encoded_password = password.encode()
                                    found_password[:PASSWORD_LENGTH] = encoded_password
                                    found_event.set()
                                    global end_time
                                    end_time = time.time()
                                    print(f"[Process-{process_id}] 비밀번호 발견: {password}")
                        return
                    except:
                        pass
                password_queue.task_done()
            except multiprocessing.queues.Empty:
                continue
    except zipfile.BadZipFile as e:
        print(f"[Process-{process_id}] ZIP 파일 오류: {e}")
    except Exception as e:
        print(f"[Process-{process_id}] 프로세스 오류: {e}")
    finally:
        print(f"[Process-{process_id}] 종료")

def generate_password_queue(charset, length):
    password_queue = multiprocessing.Queue()
    for p in permutations(charset, length):
        password_queue.put(p)
    return password_queue

def main():
    global start_time, end_time
    start_time = time.time()
    zip_memory_data = None

    try:
        with open(zip_path, 'rb') as f:
            zip_memory_data = f.read()
    except FileNotFoundError:
        print(f"Error: 파일 '{zip_path}'를 찾을 수 없습니다.")
        return

    password_queue = generate_password_queue(CHARSET, PASSWORD_LENGTH)
    num_passwords = len(CHARSET)
    factorial_length = 1
    for i in range(PASSWORD_LENGTH):
        factorial_length *= (num_passwords - i)
    print(f"생성된 총 비밀번호 개수 (중복 없음): {factorial_length:,}")

    processes = []
    for i in range(NUM_PROCESSES):
        process = multiprocessing.Process(target=crack_process, args=(i + 1, password_queue, zip_memory_data))
        processes.append(process)
        process.start()

    # 모든 작업이 큐에서 완료될 때까지 대기
    password_queue.join()

    # 비밀번호가 발견되지 않았으면 이벤트 설정 (혹시 worker가 모두 종료되었지만 찾지 못한 경우)
    if not found_event.is_set():
        found_event.set()

    for process in processes:
        process.join()

    end_time = time.time()
    elapsed_time = end_time - start_time

    if found_event.is_set():
        with found_password.get_lock():
            if found_password[:]:
                print(f"\n최종 비밀번호: {found_password[:].decode()}")
                print(f"소요 시간: {elapsed_time:.2f} 초")
            else:
                print("\n비밀번호를 찾지 못했습니다.")
                print(f"총 소요 시간: {elapsed_time:.2f} 초")
    else:
        print("\n비밀번호를 찾지 못했습니다.")
        print(f"총 소요 시간: {elapsed_time:.2f} 초")

if __name__ == "__main__":
    main()