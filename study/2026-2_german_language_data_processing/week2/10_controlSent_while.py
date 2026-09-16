"""
Python 제어문: while
"""

# 열번찍어 안 넘어가는 나무 없다
"""
treeHit = 0
while treeHit < 10:
    treeHit += 1
    print(f"나무를 {treeHit}번 찍었습니다.")
print("나무가 넘어갔습니다.")
"""

# while문 강제로 빠져나가기: 커피 자판기
"""
# 커피는 300원
coffee = 10 #커피 자판기에 남아있는 커피의 양
while True:
    money = int(input("돈을 넣어주세요: "))
    if money == 300:
        print("커피를 드릴게요.")
        coffee -= 1
    if money > 300:
        print(f"거스름돈은 {money - 300}원입니다.")
        print(f"커피를 드릴게요.")
        coffee -= 1
    else:
        print(f"커피는 300원입니다. 넣으신 돈이 부족합니다.")
        print(f"남은 커피의 양은 {coffee}개입니다.")
    if coffee == 0:
        print("커피가 다 떨어졌어요. 판매를 중지합니다.") 
        break
"""

#while문의 맨 처음으로 돌아가기
"""
a = 0
while a < 10:
    a += 1
    if a % 2 == 0: continue
    print(a)
"""