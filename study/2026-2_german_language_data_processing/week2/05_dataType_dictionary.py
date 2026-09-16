"""
Python 데이터 타입: 딕셔너리
"""

a = {1: 'a'}

" 딕셔너리의 쌍 추가하기"
a[2] = 'b'
print(a)

a['name'] = 'pey'
print(a)

a[3] = [1, 2, 3]
print(a)

" 딕셔너리 요소 제거하기 "
del a[1]
print(a)

" 딕셔너리에서 Key 사용해 Value 얻기"
print(a[2])
print(a['name'])
print(a[3])

" 딕셔너리 관련 함수: 딕셔너리변수.함수명()"
" Key 리스트 만들기(keys)"
print(a.keys())
print(list(a.keys())) #리스트로 변환하기

" Value 리스트 만들기(values)"
print(a.values())
print(list(a.values()))

" Key-Value 쌍 리스트 만들기(items)"
print(a.items())
print(list(a.items()))

" Key-Value 쌍 모두 지우기(clear)"
a.clear()
print(a)

b = {1: 'a', 2: 'b', 'name': 'pey', 3: [1, 2, 3]}
" Key로 Value 얻기(get)"
print(b.get(2))
print(b.get('name'))
print(b.get(3))