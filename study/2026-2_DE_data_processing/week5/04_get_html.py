# ==========================================================
# 웹페이지 요청 및 HTML 가져오기
#
# 브라우저가 주소창에 주소를 넣고 Enter를 누르는 일을
# 파이썬 코드로 하는 단계입니다.
#
# 기능:
# 1. requests를 사용해 웹페이지에 요청을 보낸다.
# 2. 응답 상태 코드를 확인한다.
# 3. HTML 원문 일부를 출력해 구조를 확인한다.
#
# 용어 안내:
# - HTML: 웹페이지의 뼈대(제목, 문단, 링크 등이 태그로 적힌 문서)
# - 상태 코드: 서버가 요청을 어떻게 처리했는지 알려 주는 숫자
#   (200=성공, 404=페이지 없음, 403=접근 거부)
# ==========================================================

import requests  # 웹페이지 내용을 받아오는 라이브러리


url = "https://www.tagesschau.de/"

# User-Agent: "나는 어떤 브라우저처럼 접속한다"는 소개입니다.
# 일부 사이트는 소개가 없으면 요청을 거절할 수 있습니다.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}

# GET 요청: 페이지를 "읽어 달라"고 서버에 부탁합니다.
# timeout=10: 10초 안에 답이 없으면 중단합니다.
response = requests.get(url, headers=headers, timeout=10)

# 상태 코드가 200이 아니면(실패하면) 오류를 발생시켜 프로그램을 멈춥니다.
response.raise_for_status()

print("=== 웹페이지 요청 결과 ===")
print(f"상태 코드: {response.status_code}")
print()

print("=== HTML 일부 미리보기 ===")
# 전체 HTML은 매우 길 수 있어, 앞부분 1000글자만 봅니다.
print(response.text[:1000])
