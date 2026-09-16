"""
Python 파일 읽고 쓰기
"""

"파일 읽기"
"전체 내용 읽기: read()"
"""
file = open("user_fileReadWrite_example.txt", "r", encoding="utf-8")
content = file.read()
print(content)
file.close()
"""

"한 줄씩 읽기: readline()"
"""
file = open("user_fileReadWrite_example.txt", "r", encoding="utf-8")
line1 = file.readline()
line2 = file.readline()
print(line1)
print(line2)
file.close()
"""

"한 줄씩 읽기: readline() 모든 줄을 읽어서 화면에 출력"
"""
file = open("user_fileReadWrite_example.txt", "r", encoding="utf-8")
while True:
    line = file.readline()
    if not line: break
    print(line)
file.close()
"""

"모든 줄을 리스트로 읽기: readlines()"
"""
file = open("user_fileReadWrite_example.txt", "r", encoding="utf-8")
lines = file.readlines()
print(lines)
file.close()
"""

"반복문으로 한 줄씩 읽기"
"""
file = open("user_fileReadWrite_example.txt", "r", encoding="utf-8")
for line in file:
    print(line)
file.close()
"""

"더 좋은 방식: with open()"
"""
with open("user_fileReadWrite_example.txt", "r", encoding="utf-8") as file:
    for line in file:
        print(line.strip())
"""

"파일 쓰기"
"새 파일에 쓰기: write()"
"""
file = open("user_fileReadWrite_output.txt", "w", encoding="utf-8")
file.write("Hello, Python!\n")
file.write("파일 쓰기 연습입니다.\n")
file.close()
"""

"변수 내용을 파일에 저장하기"
"""
name = "Mina"
score = 95
file = open("user_fileReadWrite_output.txt", "w", encoding="utf-8")
file.write(f"이름: {name}\n")
file.write(f"점수: {score}\n")
file.close()
"""

"파일에 내용 추가하기"
"""
file = open("user_fileReadWrite_output.txt", "a", encoding="utf-8")
file.write("새로운 기록이 추가되었습니다.\n")
file.close()
"""

"with open()으로 파일 쓰기"
"""
with open("user_fileReadWrite_output.txt", "w", encoding="utf-8") as file:
    file.write("Python file I/O\n")
    file.write("자동으로 파일이 닫힙니다.\n")
"""