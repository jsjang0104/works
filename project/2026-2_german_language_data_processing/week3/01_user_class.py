"""
Python 클래스

클래스(class)는 비슷한 특징을 가진 데이터를 묶어서 다루는 '설계도'입니다.
이 설계도로 만든 실제 결과물을 객체(object) 또는 인스턴스(instance)라고 합니다.

비유:
    클래스 = 학생증 양식
    객체   = 그 양식으로 만든 Mina의 학생증, Jisoo의 학생증
"""

# ============================================================
# 기본 구조
# ============================================================
# __init__() : 객체가 만들어질 때 자동으로 실행되는 특별한 함수.
#              '생성자(constructor)'라고 부릅니다.
# self       : 지금 만들어진 그 객체 자신.
#              메서드(클래스 안의 함수) 첫 번째 매개변수로 꼭 씁니다.


# ============================================================
# 예 1: 학생 정보를 담는 Student 클래스
# ============================================================

class Student:
    # Student 객체를 만들 때 이름과 나이를 받습니다.
    # 예: Student("Mina", 22) 를 실행하면 아래 __init__이 자동으로 호출됩니다.
    def __init__(self, name, age):
        # self.name : 이 객체만의 이름 저장 공간
        # 오른쪽 name : 함수로 전달받은 값
        self.name = name
        self.age = age

    # 객체 안에 들어 있는 이름과 나이를 이용해 자기소개를 출력합니다.
    # 호출할 때: student1.introduce()
    # 여기서 self는 자동으로 student1이 됩니다.
    def introduce(self):
        print(f"안녕하세요. 제 이름은 {self.name}이고, 나이는 {self.age}세입니다.")


# Student 설계도로 실제 학생 객체 2개를 만듭니다.
student1 = Student("Mina", 22)   # student1.name = "Mina", student1.age = 22
student2 = Student("Jisoo", 24)  # student2.name = "Jisoo", student2.age = 24

# 점(.)을 찍으면 그 객체 안의 값에 접근할 수 있습니다.
print(student1.name)   # Mina
print(student2.age)    # 24

# 메서드를 호출하면 그 객체 자신의 정보를 사용합니다.
student1.introduce()   # 안녕하세요. 제 이름은 Mina이고, 나이는 22세입니다.


# ============================================================
# 예 2: 책 정보를 담는 Book 클래스
# ============================================================

class Book:
    # 책을 만들 때 제목, 저자, 가격을 받습니다.
    def __init__(self, title, author, price):
        self.title = title      # 책 제목
        self.author = author    # 저자 이름
        self.price = price      # 가격(원)

    # 이 책의 정보를 한 번에 출력합니다.
    def show_info(self):
        print(f"제목: {self.title}")
        print(f"저자: {self.author}")
        print(f"가격: {self.price}원")


# Book 설계도로 실제 책 객체 2개를 만듭니다.
book1 = Book("파이썬 기초", "홍길동", 18000)
book2 = Book("데이터 분석 입문", "김철수", 22000)

# 각 객체의 show_info()를 호출하면, 그 책만의 정보가 출력됩니다.
book1.show_info()
print()            # 빈 줄 하나 출력해서 두 책 정보를 구분합니다.
book2.show_info()
