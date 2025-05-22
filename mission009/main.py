def _get_shifted_char(char, shift, alphabet_count):
    """
    단일 문자를 시저 암호 방식으로 shift하여 반환한다.
    """
    if 'a' <= char <= 'z':
        base = ord('a')
    elif 'A' <= char <= 'Z':
        base = ord('A')
    else:
        return char  # 알파벳이 아닌 문자는 그대로 반환

    decoded_char_code = ord(char) - shift
    if decoded_char_code < base:
        decoded_char_code += alphabet_count
    return chr(decoded_char_code)

def caesar_cipher_decode(target_text, dictionary):
    """
    시저 암호를 해독하는 함수.
    모든 가능한 자리수(알파벳 수만큼)에 대해 해독을 시도하고 결과를 (shift, 해독된 텍스트) 튜플 리스트로 반환한다.
    사전에 있는 단어가 발견될 경우 해당 결과를 반환하고 반복을 중단한다.
    """
    alphabet_count = 26  # Manually set alphabet count as string.ascii_lowercase is removed
    all_decoded_results = []
    
    for shift in range(alphabet_count):
        decoded_text = "".join([_get_shifted_char(char, shift, alphabet_count) for char in target_text])
        all_decoded_results.append((shift, decoded_text))
        print(f"Shift {shift}: {decoded_text}")

        decoded_text_lower = decoded_text.lower()
        for word in dictionary:
            if word.lower() in decoded_text_lower:
                print(f"\n사전 단어 '{word}' 발견! Shift {shift}에서 해독이 완료되었습니다.")
                return all_decoded_results, shift, decoded_text # 모든 결과와 찾은 결과 반환

    return all_decoded_results, None, None # 사전에 일치하는 단어를 찾지 못한 경우

def main():
    """
    메인 함수: password.txt를 읽고, 시저 암호를 해독하며, 결과를 파일에 저장한다.
    사전 단어 일치 시 자동 저장 기능을 포함한다.
    """
    text_dictionary = []

    password_content = ""
    try:
        with open('mission009/password.txt', 'r') as file:
            password_content = file.read().strip()
    except FileNotFoundError:
        print("Error: password.txt 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"Error reading password.txt: {e}")
        return

    if not password_content:
        print("password.txt 파일이 비어있습니다.")
        return

    print("--- 시저 암호 해독 결과 ---")
    all_decoded_results, found_shift, found_decoded_text = caesar_cipher_decode(password_content, text_dictionary)
    print("--------------------------")

    if found_decoded_text:
        # 사전을 통해 암호가 자동으로 해독된 경우
        try:
            with open('mission009/result.txt', 'w') as result_file:
                result_file.write(found_decoded_text)
            print(f"해독된 암호 '{found_decoded_text}'가 result.txt에 자동으로 저장되었습니다.")
        except Exception as e:
            print(f"Error writing to result.txt: {e}")
    else:
        # 사전을 통해 암호가 해독되지 않은 경우, 사용자에게 수동으로 입력받음
        print("사전에 일치하는 단어를 찾지 못했습니다. 수동으로 올바른 암호를 선택하세요.")
        alphabet_count = 26  # Manually set alphabet count
        while True:
            try:
                shift_input = input(f"올바른 암호라고 생각되는 자리수(Shift)를 입력하세요 (0-{alphabet_count - 1}): ")
                selected_shift = int(shift_input)
                if 0 <= selected_shift < alphabet_count:
                    # 미리 저장된 결과에서 찾아 사용
                    final_decoded_text = ""
                    for s, text in all_decoded_results:
                        if s == selected_shift:
                            final_decoded_text = text
                            break

                    try:
                        with open('mission009/result.txt', 'w') as result_file:
                            result_file.write(final_decoded_text)
                        print(f"해독된 암호 '{final_decoded_text}'가 result.txt에 저장되었습니다.")
                        break
                    except Exception as e:
                        print(f"Error writing to result.txt: {e}")
                else:
                    print(f"잘못된 자리수입니다. 0부터 {alphabet_count - 1} 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("잘못된 입력입니다. 숫자를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n프로그램을 종료합니다.")
                break

if __name__ == "__main__":
    main()