"""
Python 데이터 타입: 튜플
"""

a = ('Ich', 'lerne', 'die', 'Verarbeitung', 'deutscher', 'Sprachdaten.')

" 튜플의 인덱싱"
print(a[0])
print(a[3])

" 튜플의 슬라이싱"
print(a[0:3])
print(a[3:])
print(a[:3])

" 튜플 연산하기"
b = ('Außerdem', 'lerne', 'ich', 'auch', 'Künstliche', 'Intelligenz.')

" 튜플 더하기"
print(a + b)

" 튜플 곱하기"
print(a * 2)

" 튜플 길이 구하기: len(튜플변수)"
print(len(a))