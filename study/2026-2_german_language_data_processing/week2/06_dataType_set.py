"""
Python 데이터 타입: 집합
"""

s1 = set([1,2,3])
print(s1)

s2 = set("Hello")
print(s2)

" set의 인덱싱을 하려면 리스트나 튜플로 변환한 후 접근해야 한다."
#print(s1[0])
print(list(s1)[0])


s1 = set([1, 2, 3, 4, 5, 6])
s2 = set([4, 5, 6, 7, 8, 9])
" 교집합"
print(s1 & s2)
print(s1.intersection(s2))

" 합집합"
print(s1 | s2)
print(s1.union(s2))

" 차집합"
print(s1 - s2)
print(s1.difference(s2))

" 집합 관련 함수: 집합변수.함수명()"
"값 1개 추가하기(add)"
s1.add(7)
print(s1)

"값 여러개 추가하기(update)"
s1.update([8, 9, 10])
print(s1)

"특정값 제거하기(remove)"
s1.remove(3)
print(s1)