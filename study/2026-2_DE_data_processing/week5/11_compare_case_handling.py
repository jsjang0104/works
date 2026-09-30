# ==========================================================
# 대문자 처리 방식 비교
#
# 영어 분석에서는 모든 글자를 소문자로 바꾸는 일이 흔합니다.
# 독일어는 명사를 대문자로 쓰기 때문에, 소문자화하면
# "이 단어가 명사였다"는 정보가 사라질 수 있습니다.
#
# 기능:
# 1. 원문 유지, 전체 소문자화, 문장 첫 글자 대문자화 결과를 비교한다.
# 2. 독일어 명사 대문자 정보가 어떻게 달라지는지 관찰한다.
#
# 용어 안내:
# - lower(): 모든 글자를 소문자로 바꿈
# - capitalize(): 문자열의 첫 글자만 대문자, 나머지는 소문자
# ==========================================================


sample_text = "Das Haus ist groß. Viele Menschen besuchen die Universität in Berlin."

original_text = sample_text                 # 원문 그대로
lower_text = sample_text.lower()            # 전부 소문자
capitalized_text = sample_text.capitalize() # 맨 앞 한 글자만 대문자

print("=== 원문 유지 ===")
print(original_text)

print("\n=== 전체 소문자화 ===")
print(lower_text)

print("\n=== 문장 첫 글자만 대문자화(capitalize) ===")
print(capitalized_text)

print("\n=== 관찰 포인트 ===")
print("- 'Haus', 'Menschen', 'Universität'와 같은 명사의 대문자 정보가 소문자화에서 사라진다.")
print("- 독일어에서는 대문자 정보가 문법적 단서가 될 수 있다.")
