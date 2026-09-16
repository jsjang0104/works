"""
Python 함수
"""

# 함수의 구조
"""
def add(a, b):
    result = a + b
    return result
print("합계:", add(5, 3))
"""

# 입력값이 몇 개가 될지 모르는 경우: *args
"""
def add_many(*args):
    result = 0
    for i in args:
        result += i
    return result
print("합계:", add_many(1, 2, 3, 4, 5))
"""

# 함수의 결과값은 언제나 하나.
"""
def add_and_mul(a, b):
    return a + b, a * b

result1, result2 = add_and_mul(3, 4)
print("합계:", result1)
print("곱셈:", result2)
"""

#함수 안에서 선언한 변수의 효력 범위: 지역변수와 전역변수
"""
a = 1 # 전역변수
def vartest(a):
    a += 1 # 지역변수
    return a
print("지역변수:", vartest(a))  
print("전역변수:", a)
"""

# lambda 함수: 이름 없이, 한 줄로 만든 간단한 함수
# lambda 매개변수1, 매개변수2, ...: 매개변수를 이용한 표현식
"""
result = lambda a, b: a + b
print("합계:", result(5, 3))
"""

#독일어 텍스트 데이터에서도 단어 길이, 빈도, 특정 속성을 기준으로 정렬할 때 사용
"""
words = ["Haus", "Geschwindigkeit", "Buch", "Donaudampfschifffahrt"]
result = sorted(words, key=lambda word: len(word))
print(result)
"""