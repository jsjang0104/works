# ==========================================================
# 필요한 텍스트 요소 추출하기
#
# HTML 원문에는 태그(<p>, <title> 등)가 섞여 있습니다.
# BeautifulSoup으로 "제목"과 "문단"만 골라 꺼냅니다.
#
# 기능:
# 1. BeautifulSoup으로 HTML을 파싱한다.
# 2. 페이지 제목(title)과 문단(p 태그)을 추출한다.
# 3. 추출 결과 일부를 출력해 확인한다.
#
# 용어 안내:
# - 파싱(parsing): 긴 HTML 문자열을 태그 구조로 나누어 이해하는 일
# - 태그: <p>문단</p> 처럼 내용을 감싸는 HTML 표시
# ==========================================================

import requests
from bs4 import BeautifulSoup  # HTML에서 원하는 태그만 찾는 도구


url = "https://www.tagesschau.de/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()
html = response.text  # 서버가 보내 준 HTML 원문(문자열)

# html.parser: 파이썬에 기본으로 들어 있는 HTML 해석기
soup = BeautifulSoup(html, "html.parser")

# ----------------------------------------------------------
# 1. 페이지 제목 추출
#    soup.title이 없으면(제목 태그가 없으면) "제목 없음"을 씁니다.
#    get_text(strip=True): 태그 안 글자만 꺼내고 앞뒤 공백을 지웁니다.
# ----------------------------------------------------------
title = soup.title.get_text(strip=True) if soup.title else "제목 없음"

# ----------------------------------------------------------
# 2. 모든 문단(p 태그) 추출
#    find_all("p"): 페이지에 있는 <p>...</p>를 모두 찾습니다.
# ----------------------------------------------------------
paragraphs = soup.find_all("p")

# ----------------------------------------------------------
# 3. 문단 텍스트만 정리하여 리스트로 저장
#    빈 문단(공백만 있는 경우)은 넣지 않습니다.
# ----------------------------------------------------------
paragraph_texts = []
for p in paragraphs:
    text = p.get_text(strip=True)
    if text:
        paragraph_texts.append(text)

print("=== 페이지 제목 ===")
print(title)
print()

print("=== 추출된 문단 5개 예시 ===")
# [:5] : 앞에서 5개만 보여 줍니다.
# enumerate(..., start=1): 번호를 1부터 붙입니다.
for i, text in enumerate(paragraph_texts[:5], start=1):
    print(f"{i}. {text}")
