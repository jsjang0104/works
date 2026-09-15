# 하위 디렉터리에서 독일어 텍스트 파일 찾기
#
# 디렉터리(directory)는 폴더와 같은 말입니다.
# 하위 디렉터리 검색이란, 어떤 폴더 안뿐 아니라
# 그 안의 폴더, 또 그 안의 폴더까지 모두 살펴보는 일입니다.
#
# 비유:
#     폴더     = 책장
#     파일     = 책장 안에 꽂힌 책
#     하위 폴더 = 책장 안의 작은 서랍
#     rglob()  = "이 책장과 서랍 안까지 전부 뒤져 주세요"

from pathlib import Path  # 파일/폴더 경로를 다루는 표준 도구입니다.
import tempfile  # 실습이 끝나면 자동으로 지워지는 임시 폴더를 만듭니다.

# with 문: 이 블록이 끝나면 임시 폴더가 자동으로 삭제됩니다.
# 실제 프로젝트에서는 Path("나의_코퍼스_폴더")처럼 바꾸어 사용할 수 있습니다.
with tempfile.TemporaryDirectory() as temp_folder:
    # Path()에 폴더 경로를 넣으면, 그 폴더를 시작점으로 다룰 수 있습니다.
    base_folder = Path(temp_folder)

    # / 기호로 폴더 이름을 이어 붙입니다. (Windows의 \ 와 같은 역할)
    # mkdir()은 그 이름의 새 폴더를 만듭니다.
    (base_folder / "nachrichten").mkdir()  # 뉴스 폴더
    (base_folder / "literatur").mkdir()    # 문학 폴더

    # write_text()는 파일을 만들고 내용을 씁니다.
    # encoding="utf-8"은 독일어 특수문자(ä, ö, ü, ß)를 깨지지 않게 저장합니다.
    (base_folder / "nachrichten" / "artikel1.txt").write_text(
        "Deutschland und Europa", encoding="utf-8"
    )
    (base_folder / "literatur" / "gedicht.txt").write_text(
        "Ein Gedicht auf Deutsch", encoding="utf-8"
    )
    # 아래 파일은 .csv 이므로, 나중에 *.txt 검색에서는 나오지 않습니다.
    (base_folder / "literatur" / "notiz.csv").write_text(
        "wort,haeufigkeit\nHaus,3", encoding="utf-8"
    )

    # rglob()의 r은 recursive(재귀적)의 뜻입니다.
    # 한 단계만 보지 않고, 안쪽 폴더까지 계속 들어가며 찾습니다.
    # "*.txt" → 이름이 .txt로 끝나는 파일만 찾습니다.
    # list()로 감싸면, 찾은 파일들을 목록으로 한꺼번에 보관합니다.
    text_files = list(base_folder.rglob("*.txt"))

    print("===== 찾은 독일어 텍스트 파일 =====")
    for file_path in text_files:
        # relative_to()는 시작 폴더를 뺀 상대 경로만 보여 줍니다.
        # 예: C:\...\literatur\gedicht.txt  →  literatur\gedicht.txt
        print(file_path.relative_to(base_folder))

        # read_text()는 파일 내용을 문자열로 읽어 옵니다.
        print("내용:", file_path.read_text(encoding="utf-8"))
        print("-" * 30)  # 구분선(하이픈 30개)을 출력합니다.

    # len()은 목록에 들어 있는 항목 개수입니다. 여기서는 .txt 파일 수입니다.
    print(f"총 .txt 파일 수: {len(text_files)}")
