"""
Python 데이터 타입: 불리언(Boolean)
"""

" 불리언 값 생성"
a = True
b = False

" 불리언 값 출력"
print(a)
print(b)

" 불리언 타입"
print(type(a))
print(type(b))

" 불리언 연산"
print(1 == 1)  # True
print(2 > 1)  # True
print(1 > 2)  # False

print(bool('python'))  # True
print(bool(''))  # False
print(bool([1, 2, 3]))  # True
print(bool([]))  # False
print(bool(0))  # False
print(bool(None))  # False
print(bool(1))  # True