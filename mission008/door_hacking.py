import zipfile
import threading
import time

charset = "etaoinshrdlucmfwypvbgkqjxz0123456789"
password_length = 6
zip_path = 'mission008/file/emergency_storage_key.zip'

found_event = threading.Event()
found_password = None
lock = threading.Lock()
start_time = 0
end_time = 0

def is_within_max_dup(password, max_dup=2):
    return all(password.count(c) <= max_dup for c in set(password))

def generate_passwords_with_prefix(prefix, charset, length):
    if length == 0:
        yield prefix
    else:
        for c in charset:
            yield from generate_passwords_with_prefix(prefix + c, charset, length - 1)

def crack_thread(thread_id, fixed_char):
    global found_password, end_time
    try:
        zip_file = zipfile.ZipFile(zip_path)
    except Exception as e:
        print(f"[Thread-{thread_id}] ZIP 열기 실패: {e}")
        return

    print(f"[Thread-{thread_id}] 시작 문자 '{fixed_char}'로 시도")

    for password in generate_passwords_with_prefix(fixed_char, charset, password_length - 1):
        if found_event.is_set():
            return
        if not is_within_max_dup(password):
            continue
        try:
            zip_file.extractall(pwd=password.encode())
            with lock:
                if not found_event.is_set():
                    found_password = password
                    found_event.set()
                    end_time = time.time()
                    print(f"[Thread-{thread_id}] 비밀번호 발견: {password}")
            return
        except:
            continue

    print(f"[Thread-{thread_id}] 비밀번호 찾기 실패")

def main():
    global start_time, end_time
    start_time = time.time()
    threads = []
    for i, ch in enumerate(charset):
        t = threading.Thread(target=crack_thread, args=(i+1, ch))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = time.time()
    elapsed_time = end_time - start_time

    if found_password:
        print(f"\n최종 비밀번호: {found_password}")
        print(f"소요 시간: {elapsed_time:.2f} 초")
    else:
        print("\n비밀번호를 찾지 못했습니다.")
        print(f"총 소요 시간: {elapsed_time:.2f} 초")

if __name__ == "__main__":
    main()