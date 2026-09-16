"""
Python 데이터 타입: 변수(Variable)
"""

" 변수 값 생성"
a = [1, 2, 3]
b = a

" 변수 값 출력"
#print(id(a))
#print(id(b))

"변수를 만드는 여러 가지 방법"
"튜플처럼"
a, b, c = (1, 2, 3)
#print(a, b, c)

"리스트"
[d, e, f] = [4, 5, 6]
#print(d, e, f)

"여러개의 변수에 값은 값을 대입"
g = h = i = 7
#print(g, h, i)

" 두 변수의 값을 아주 간단히 바꾸는 방법"
j = 8
k = 9
j, k = k, j
#print(j)
#print(k)

" 서로 다른 메모리를 가리킴"
m = [1, 2, 3]
n = [1, 2, 3]
#print(m is n)  # False
#print(m == n)  # True
