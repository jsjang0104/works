# 예외 처리로 안전한 독일어 단어 입력 프로그램 만들기
# 숫자 입력 오류와 빈 문자열 입력을 구분하여 처리합니다.

def get_positive_number(message):
    """사용자가 1 이상의 정수를 입력할 때까지 반복해서 묻습니다."""
    while True:
        try:
            number = int(input(message))
            if number < 1:
                # 숫자이지만 조건에 맞지 않을 때 직접 ValueError를 발생시킵니다.
                raise ValueError
            return number
        except ValueError:
            print("오류: 1 이상의 정수를 입력하세요.")

print("독일어 단어장 입력 프로그램")
count = get_positive_number("저장할 독일어 단어 수를 입력하세요: ")
vocabulary = []

for index in range(count):
    while True:
        word = input(f"{index + 1}번째 독일어 단어: ").strip()
        if word:
            vocabulary.append(word)
            break
        print("오류: 빈 단어는 저장할 수 없습니다.")

print("\n===== 저장된 단어 =====")
for index, word in enumerate(vocabulary, start=1):
    print(f"{index}. {word}")
