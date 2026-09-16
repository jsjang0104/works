"""
Python 제어문: for
"""

" 전형적인 for문"
"""
test_list = ["one", "two", "three"]
for i in test_list:
    print(i)
"""

"다양한 for문의 사용"
"""
a = [(1, 2), (3, 4), (5, 6)]
for (first, last) in a:
    print(first + last)
"""

" for문의 응용: 60점 이상이면 합격, 미만이면 불합격"
"""
marks = [90, 25, 67, 45, 80] # 학생들의 시험 점수 리스트
number = 0 # 학생에게 붙여 줄 번호
for mark in marks:
    number += 1
    if mark >= 60:
        print(f"{number}번 학생은 {mark}점으로 합격입니다.")
    else:
        print(f"{number}번 학생은 {mark}점으로 불합격입니다.")
"""

" for문과 continue"
"""
marks = [90, 25, 67, 45, 80] # 학생들의 시험 점수 리스트
number = 0 # 학생에게 붙여 줄 번호
for mark in marks:
    number += 1
    if mark < 60:
        continue
    print(f"{number}번 학생은 {mark}점으로 합격입니다.")
"""
    
" for문과 range함수"
"""
a = range(10) # 0~9까지의 숫자를 생성
for i in a:
    print(i)
"""

" for문과 range함수 응용"
"""
marks = [90, 25, 67, 45, 80] # 학생들의 시험 점수 리스트
for number in range(len(marks)):
    if marks[number] < 60:
        continue
    print(f"{number + 1}번 학생은 {marks[number]}점으로 합격입니다.")
"""

" for문과 range를 사용한 구구단 출력"
"""
for i in range(2, 10): # 2~9까지의 숫자
    for j in range(1, 10): # 1~9까지의 숫자
        print(f"{i} * {j} = {i * j}")
    print("") # 단이 바뀔 때마다 한 줄 띄기
"""

" 리스트 내포(List Comprehension)"
" 리스트 내포를 사용하지 않은 경우"
"""
a = [1, 2, 3, 4]
result = []
for i in a:
    result.append(i * 2)
print(result)
"""

" 리스트 내포를 사용한 경우"
"""
a = [1, 2, 3, 4]
result = [i * 2 for i in a]
print(result)
"""