# ==========================================================
# 추출 텍스트를 TXT로 저장하기
#
# 화면에만 출력하면 프로그램이 끝나면 사라집니다.
# 문단을 텍스트 파일로 남겨 다음 실습에서 다시 읽게 합니다.
#
# 기능:
# 1. 웹페이지에서 문단 텍스트를 추출한다.
# 2. 추출한 텍스트를 하나의 TXT 파일로 저장한다.
# 3. UTF-8 인코딩으로 저장하여 독일어 특수문자를 보존한다.
#
# 용어 안내:
# - 인코딩: 글자를 컴퓨터 숫자로 저장하는 방식
# - UTF-8: 한글, 독일어 움라우트(ä, ö, ü), ß까지 담을 수 있는 방식
# ==========================================================

import requests
from bs4 import BeautifulSoup


url = "https://www.tagesschau.de/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
paragraphs = soup.find_all("p")

# 비어 있지 않은 문단만 리스트에 모읍니다.
paragraph_texts = []
for p in paragraphs:
    text = p.get_text(strip=True)
    if text:
        paragraph_texts.append(text)

output_file = "german_webpage_text.txt"

# "w": 쓰기 모드 (같은 이름 파일이 있으면 내용을 덮어씁니다)
# encoding="utf-8": ä, ö, ü, ß, 한글이 깨지지 않게 저장합니다.
# with: 파일을 다 쓰면 자동으로 닫아 줍니다.
with open(output_file, "w", encoding="utf-8") as f:
    for text in paragraph_texts:
        f.write(text + "\n")  # 문단 하나마다 줄바꿈을 넣습니다.

print("=== TXT 저장 완료 ===")
print(f"저장 파일명: {output_file}")
print(f"저장된 문단 수: {len(paragraph_texts)}")
