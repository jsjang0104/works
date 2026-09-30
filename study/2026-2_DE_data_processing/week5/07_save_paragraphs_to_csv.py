# ==========================================================
# 문장 또는 문단 단위로 CSV 저장하기
#
# TXT는 "글이 이어진 파일"이고,
# CSV는 엑셀처럼 "칸(열)이 나뉜 표"입니다.
# 문단마다 번호를 붙여 나중에 분석하기 쉽게 저장합니다.
#
# 기능:
# 1. 웹페이지에서 문단 텍스트를 추출한다.
# 2. 각 문단에 번호를 부여하여 CSV 파일로 저장한다.
# 3. 필요에 따라 문장 단위 저장으로 확장할 수 있다.
#
# 용어 안내:
# - CSV: Comma-Separated Values. 쉼표로 칸을 나눈 표 파일
# - utf-8-sig: 엑셀이 한글/독일어를 깨지지 않게 열도록 하는 UTF-8
# ==========================================================

import csv        # CSV 파일을 쉽게 쓰기 위한 파이썬 기본 모듈
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

paragraph_texts = []
for p in paragraphs:
    text = p.get_text(strip=True)
    if text:
        paragraph_texts.append(text)

output_file = "german_webpage_paragraphs.csv"

# newline="": 윈도우에서 빈 줄이 두 줄씩 들어가는 현상을 막습니다.
# utf-8-sig: 엑셀에서 열어도 한글·독일어가 깨지지 않게 합니다.
with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)

    # 첫 줄은 열 이름(헤더)입니다.
    writer.writerow(["번호", "문단텍스트"])

    # start=1: 번호를 0이 아니라 1부터 매깁니다.
    for idx, text in enumerate(paragraph_texts, start=1):
        writer.writerow([idx, text])

print("=== CSV 저장 완료 ===")
print(f"저장 파일명: {output_file}")
print(f"저장된 문단 수: {len(paragraph_texts)}")
