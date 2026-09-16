"""
Python 사용자 입력과 출력
"""

"print(출력할 내용)"
# 문자열 출력
#print("Python")
#print('독일어 데이터 처리')

"숫자 출력"
#print(100)
#print(25 + 5)
#print(10 / 2)

"변수 출력"
name = "Mina"
age = 22
#print(name)
#print(age)

# 여러개를 한번에 출력
ame = "Mina"
age = 22
#print(name, age)

# 쉽표를 이용해 문자열과 변수를 함께 출력하기
name = "Mina"
#print("이름은", name, "입니다.")

# 문자열 연결(+)을 이용해 문자열과 변수를 함께 출력하기
name = "Mina"
#print("이름은 " + name + "입니다.")

age = 22
#print("나이는 " + age + "살입니다.") #+로 연결할 때는 문자열끼리만 연결 가능

age = 22
#print("나이는 " + str(age) + "살입니다.")

# f-string을 사용하는 방법
name = "Mina"
age = 22
#print(f"이름은 {name}이고, 나이는 {age}살입니다.")

#줄바꿈과 관련된 출력
#print("첫째 줄")
#print("둘째 줄")

#줄바꿈 없이 출력하기: end
#print("Hello", end=" ")
#print("Python")

#print("A", end="-")
#print("B", end="-")
#print("C")

# 구분자 설정: sep, 여러 값을 출력할 때 값 사이에 들어갈 문자를 바꿀 수 있다.
#print("2026", "07", "08", sep="-")
#print("apple", "banana", "cherry", sep=", ")

# 특수문자 사용: 줄바꿈 \n
#print("독일어\n영어\n한국어")

# 특수문자 사용: 탭 \t
#print("이름\t점수")
#print("Mina\t95")


## 사용자 입력
"""
name = input("Wie heißen Sie? ")
print(name)
"""

#input()으로 입력받은 값은 항상 문자열(string)
"""
age = input("나이를 입력하세요: ") #오류 발생
print(age + 1)
"""

#올바른 예: int() 사용
"""
age = int(input("나이를 입력하세요: "))
print(age + 1)
"""

#실수를 입력받는 경우: float() 사용
"""
height = float(input("키를 입력하세요(cm): "))
print(height)
"""

# input()과 print()의 결합: 사용자의 여러 입력과 출력
"""
name = input("Wie heißen Sie? ")
stadt = input("Wo wohnen Sie? ")
alter = input("Wie alt sind Sie? ")
print(f"Ich heiße {name}. Ich wohne in {stadt}. Ich bin {alter} Jahre alt.")
"""