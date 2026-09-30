# ==========================================================
# 독일어 웹페이지 robots.txt 확인
#
# 웹사이트를 크롤링하기 전에, 사이트가 "어디를 방문해도 되는지"
# 적어 둔 안내문(robots.txt)을 먼저 확인합니다.
#
# 기능:
# 1. robots.txt 다운로드
# 2. robots.txt 내용 출력
# 3. robots.txt 주요 규칙 분석
# 4. 접근 가능한 URL인지 확인
#
# 용어 안내:
# - robots.txt: 검색 로봇/크롤러에게 허용·차단 경로를 알려 주는 파일
# - User-agent: 규칙을 적용할 대상 (예: * 는 모든 로봇)
# - Allow / Disallow: 허용 경로 / 차단 경로
# ==========================================================

import requests                          # 웹에서 파일을 받아올 때 사용
from urllib.robotparser import RobotFileParser  # robots.txt 규칙을 해석하는 도구


# ==========================================================
# 1. robots.txt 다운로드
# ==========================================================

def download_robots(site):
    """사이트 주소 뒤에 /robots.txt를 붙여 파일을 받아옵니다."""

    # 끝의 / 를 먼저 지워서 https://example.com//robots.txt 가 되지 않게 합니다.
    site = site.rstrip("/")
    robots_url = site + "/robots.txt"

    try:
        # timeout=10: 10초 안에 응답이 없으면 기다림을 중단합니다.
        response = requests.get(robots_url, timeout=10)

        # 상태 코드 200 = 성공. 그 외(404 등)는 파일이 없거나 접근 실패입니다.
        if response.status_code != 200:
            print("robots.txt가 존재하지 않습니다.")
            return None, None

        # 주소와 파일 내용(문자열)을 함께 돌려줍니다.
        return robots_url, response.text

    except Exception as e:
        print(e)
        return None, None


# ==========================================================
# 2. robots.txt 내용 출력 및 주요 규칙 해석
#    robots.txt는 보통 아래와 같은 한 줄 규칙들의 모음입니다.
#    User-agent: *
#    Disallow: /suche
# ==========================================================

def analyze_robots(text):
    """robots.txt 원문을 출력한 뒤, 주요 키워드를 한글로 풀어 설명합니다."""

    print("=" * 70)
    print("robots.txt 내용")
    print("=" * 70)

    print(text)

    print("\n")
    print("=" * 70)
    print("robots.txt 해석")
    print("=" * 70)

    current_agent = None  # 지금 읽고 있는 User-agent 이름을 기억해 둡니다.

    # splitlines(): 한 줄씩 잘라 리스트로 만듭니다.
    for line in text.splitlines():

        line = line.strip()  # 앞뒤 공백 제거

        if line == "":
            continue  # 빈 줄은 건너뜁니다.

        if line.startswith("#"):
            continue  # # 으로 시작하는 줄은 주석(설명)이므로 건너뜁니다.

        if ":" not in line:
            continue  # 키:값 형태가 아니면 규칙으로 보지 않습니다.

        # 한 번만 나누는 이유: http://... 처럼 값 안에 : 가 또 있을 수 있습니다.
        key, value = line.split(":", 1)

        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            current_agent = value
            print(f"\nUser-agent : {value}")

        elif key == "allow":
            print(f"   허용 경로     : {value}")

        elif key == "disallow":
            print(f"   차단 경로     : {value}")

        elif key == "crawl-delay":
            # 요청과 요청 사이에 몇 초를 쉬라고 하는 규칙입니다.
            print(f"   요청 간격     : {value}초")

        elif key == "sitemap":
            # 사이트맵: 사이트에 어떤 페이지가 있는지 모아 둔 주소
            print(f"\nSitemap")
            print(f"   {value}")

        elif key == "host":
            print(f"\nHost")
            print(f"   {value}")


# ==========================================================
# 3. 특정 URL이 접근 가능한지 확인
#    RobotFileParser.can_fetch()가 Allow/Disallow 규칙을 대신 계산해 줍니다.
# ==========================================================

def check_permission(site):
    """사용자가 입력한 경로가 robots.txt상 허용인지 반복해서 확인합니다."""

    parser = RobotFileParser()
    parser.set_url(site.rstrip("/") + "/robots.txt")

    try:
        parser.read()  # 규칙을 읽어 내부적으로 해석합니다.
    except:
        print("robots.txt를 읽을 수 없습니다.")
        return

    print("\n")
    print("=" * 70)
    print("URL 접근 가능 여부 확인")
    print("=" * 70)

    while True:

        path = input("\n확인할 URL 경로(exit 종료): ")

        if path.lower() == "exit":
            break

        # 경로가 / 로 시작하지 않으면 붙여 줍니다. 예: politik → /politik
        if not path.startswith("/"):
            path = "/" + path

        url = site.rstrip("/") + path

        # "*" : 모든 로봇에 적용되는 규칙을 기준으로 판단합니다.
        result = parser.can_fetch("*", url)

        if result:
            print("접근 가능")
        else:
            print("접근 금지")


# ==========================================================
# 4. 전체 실행
# ==========================================================

def main():
    """주소를 입력받아 robots.txt를 받고, 해석하고, 경로 허용 여부를 확인합니다."""

    print("=" * 70)
    print("robots.txt 분석기")
    print("=" * 70)

    site = input("사이트 주소를 입력하세요\n예) https://www.tagesschau.de/\n\n> ")

    robots_url, text = download_robots(site)

    if text is None:
        return  # 파일을 못 받았으면 여기서 종료합니다.

    print("\nrobots.txt 주소")
    print(robots_url)

    analyze_robots(text)

    check_permission(site)


# 이 파일을 직접 실행할 때만 main()이 호출됩니다.
if __name__ == "__main__":
    main()
