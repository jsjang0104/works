# 실습 5: 텍스트 파일을 읽어 간단한 분석 보고서 만들기
# 같은 폴더에 german_sample.txt 파일을 만들지 않아도 실행되도록 예시 파일을 먼저 생성한다.
file_name = "german_sample.txt"
sample_text = """Ich studiere Germanistik.
Die deutsche Sprache ist wichtig.
Ich lerne Python für die Textanalyse."""

with open(file_name, "w", encoding="utf-8") as file:
    file.write(sample_text)


def clean_word(word):
    """단어 끝의 기본 문장부호를 제거하고 소문자로 바꾼다."""
    return word.lower().strip(".,!?;:")


def count_words(text):
    """텍스트의 유효 단어 수를 반환한다."""
    words = text.split()
    valid_words = []
    for word in words:
        cleaned_word = clean_word(word)
        if cleaned_word != "":
            valid_words.append(cleaned_word)
    return valid_words


with open(file_name, "r", encoding="utf-8") as file:
    text = file.read()

lines = text.splitlines()
words = count_words(text)
keyword = "deutsche"

print("=== 독일어 텍스트 분석 보고서 ===")
print("문장/줄 수:", len(lines))
print("단어 수:", len(words))
print(f"'{keyword}' 등장 횟수:", words.count(keyword))
print("첫 번째 줄:", lines[0])

report_name = "german_text_report.txt"
with open(report_name, "w", encoding="utf-8") as report:
    report.write("=== 독일어 텍스트 분석 보고서 ===\n")
    report.write(f"문장/줄 수: {len(lines)}\n")
    report.write(f"단어 수: {len(words)}\n")
    report.write(f"'{keyword}' 등장 횟수: {words.count(keyword)}\n")

print("보고서 파일 저장 완료:", report_name)
