"""
Python 데이터 타입: 리스트
"""

a = ['Ich', 'lerne', 'die', 'Verarbeitung', 'deutscher', 'Sprachdaten.']

" 리스트의 인덱싱"
print(a)
print(a[0])
print(a[0] + a[3])
print(a[-1])

" 리스트의 슬라이싱"
print(a[0:3])
print(a[3:])

" 리스트 연산하기"
b = ['Außerdem', 'lerne', 'ich', 'auch', 'Künstliche', 'Intelligenz.']

" 리스트 더해서 연결하기(Concatenation)"
print(a + b)

" 리스트 곱하기"
print(a * 2)

" 리스트 길이 구하기: len(리스트변수)"
print(len(a))

" 리스트에서 값 수정하기"
a[-1] = 'Texte'
print(a)

"del 함수 사용해 리스트 요소 삭제하기"
del b[3]
print(b)

del b[3:]
print(b)

"리스트 관련 함수: 리스트변수.함수명()"
"리스트에 요소 추가하기(append)"
b.append('Möchtest du auch mitlernen?')
print(b)

"리스트 정렬"
b.sort()
print(b)

"리스트 뒤집기(reverse)"
b.reverse()
print(b)

"리스트 위치 반환(index)"
print(b.index('lerne'))

"리스트에 요소 삽입하기(insert)"
b.insert(1, 'Ich')
print(b)

"리스트 요소 제거하기(remove)"
b.remove('lerne')
print(b)

"리스트 요소 끄집어내기(pop)"
b.pop()
print(b)

"리스트에 포함된 요소의 개수 세기(count)"
print(b.count('Ich'))

"리스트 확장하기(extend)"
b.extend(['Ich', 'lerne', 'die', 'Verarbeitung', 'deutscher', 'Sprachdaten.'])
print(b)