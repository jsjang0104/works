# 02_독일어_NLP_모델_로드하기.py
# 독일어 형태소 분석 실습 2: 독일어 NLP 모델 또는 도구 로드하기
#
# 이 파일의 목적:
#   - spaCy에 독일어 모델을 올려, 이후 문장 분석에 쓸 nlp 객체를 만든다.
#   - 모델이 없으면 설치 안내를 출력한다 (실습 환경 점검).

import spacy

# try-except: 모델이 없을 때 프로그램이 바로 죽지 않고 안내 메시지를 보여 줌
try:
    # de_core_news_sm: 독일어 소형 모델 (속도 빠름, 실습용으로 충분)
    # 로드에 성공하면 nlp는 "문장 → Doc 분석 객체"로 바꿔 주는 파이프라인
    nlp = spacy.load("de_core_news_sm")
    # meta: 모델 이름·버전 등 메타정보 딕셔너리
    print("독일어 모델 로드 완료:", nlp.meta.get("name", "unknown"))
except OSError:
    # OSError: 지정한 모델 파일이 설치되어 있지 않을 때 주로 발생
    print("de_core_news_sm 모델이 설치되어 있지 않습니다.")
    print("다음 명령으로 설치하세요:")
    print("python -m spacy download de_core_news_sm")
