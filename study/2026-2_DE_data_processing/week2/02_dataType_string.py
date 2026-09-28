"""
Python 데이터 타입: 문자열
"""

a = "Ich studiere Germanistik."
b = 'Die Sprache ist sehr wichtig.'
c = "Ich studiere Germanistik. 'Die Sprache ist sehr wichtig.'"
d = "Ich studiere Germanistik. 'Die Sprache ist sehr wichtig.'"
e = """Life is too short, You need Python"""
f = '''Life is too short, You need Python'''
g = """
Life is too short, 
You need Python
"""
h = "   Ich studiere Germanistik.   "

print(a)
print(b)
print(c)
print(d)
print(e)
print(f)
print(g)

" 문자열 더해서 연결하기(Concatenation)"
print(a+b)

" 문자열 곱하기"
print(a * 2)

"문자열 곱하기 응용"
print("=" * 50)

"문자열 길이 구하기: len(문자열변수)"
print(len(a))

"문자열 인덱싱(Indexing)"
print(a[0])
print(a[1])
print(a[2])
print(a[3])
print(a[-1])
print(a[-2])

"문자열 슬라이싱(Slicing)"
print(a[0:3])
print(a[4:12])
print(a[:12])
print(a[12:])

"문자열 관련 함수: 문자열변수.함수명()"
"문자 개수 세기(count)"
print(a.count("i"))

"문자 위치 알려주기(find)"
print(a.find("i"))
print(a.find("o"))

"문자 위치 알려주기(index)"
print(a.index("i"))
# print(a.index("o"))

"문자열 삽입하기(join)"
print(",".join("abcd"))

"소문자를 대문자로 바꾸기(upper)"
print(a.upper())

"대문자를 소문자로 바꾸기(lower)"
print(a.lower())

"왼쪽 공백 지우기(lstrip)"
print(h.lstrip())

"오른쪽 공백 지우기(rstrip)"
print(h.rstrip())

"양쪽 공백 지우기(strip)"
print(h.strip())

"문자열 바꾸기(replace)"
print(a.replace("Germanistik", "Französisch"))

"문자열 나누기(split)"
print(a.split())