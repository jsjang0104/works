"""
Python 제어문: if
"""

" 조건문이 참"
"""
money = True
if money:
    print("택시를 타고 가라")
else:
    print("걸어가라")
"""

" 비교연산자를 이용한 if문"
"""
money = 2000
if money >= 3000:
    print("택시를 타고 가라")
else:
    print("걸어가라")
"""

" and, or, not 연산자를 이용한 if문"
"""
money = 2000
card = True
if money >= 3000 or card:
    print("택시를 타고 가라")
else:
    print("걸어가라")
"""

" x in 리스트를 이용한 if문"
"""
pocket = ["paper", "cellphone", "money"]
if "money" in pocket:
    print("택시를 타고 가라")
else:
    print("걸어가라")

pocket = ["paper", "cellphone"]
if "money" not in pocket:
    print("걸어가라")
else:
    print("택시를 타고 가라")
"""


" elif 사용"
"""
pocket = ["paper", "cellphone"]
card = True
if "money" in pocket:
    print("택시를 타고 가라")
elif card:
    print("택시를 타고 가라")
else:
    print("걸어가라")
"""