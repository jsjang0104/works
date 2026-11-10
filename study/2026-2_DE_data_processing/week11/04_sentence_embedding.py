"""04. Sentence Embedding: 문장 의미를 하나의 벡터로 표현

Sentence Embedding이란?
- 단어 하나하나가 아니라 "문장 전체"를 고정 길이 실수 벡터로 바꿉니다.
- 의미가 비슷한 문장은 벡터 공간에서 서로 가깝게 위치합니다.
- 단어 벡터를 단순 평균하는 것보다, 문장 구조를 반영한 표현을 얻는 데 유리합니다.

예)
  "Ich lerne Deutsch."
  "Ich studiere die deutsche Sprache."  ← 패러프레이즈(비슷한 의미)
  "Das Wetter ist schön."               ← 의미가 다름

필요 패키지:
  pip install sentence-transformers
"""

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


# 수업/실습에서 기본으로 쓸 다국어 문장 임베딩 모델
# - 여러 언어 문장을 같은 벡터 공간에 올려, 의미가 비슷하면 가깝게 위치하도록 학습됨
# - 처음 실행 시 모델 가중치를 인터넷에서 다운로드함
DEFAULT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# 기본 데모 문장 (독일어)
#   0번과 1번: 의미적으로 유사 (패러프레이즈)
#   2번     : 의미적으로 무관
DEFAULT_SENTENCES = [
    "Ich lerne Deutsch.",                 # 나는 독일어를 배운다
    "Ich studiere die deutsche Sprache.", # 나는 독일어를 공부한다
    "Das Wetter ist schön.",              # 날씨가 좋다
]


def load_model(model_name=DEFAULT_MODEL_NAME):
    """사전학습된 문장 임베딩 모델을 불러옵니다.

    매개변수
    - model_name: Hugging Face 등에 등록된 모델 이름

    반환값
    - SentenceTransformer 모델 객체
    """
    return SentenceTransformer(model_name)


def encode_sentences(model, sentences, convert_to_tensor=True):
    """문장 목록을 각각 하나의 밀집 벡터로 변환합니다.

    - model.encode(...) : 문장 → 고정 길이 벡터
    - convert_to_tensor=True 이면 PyTorch 텐서로 반환
      (이후 cos_sim 계산에 바로 쓰기 편함)

    반환값 shape 예: (문장 개수, 임베딩 차원)
    - paraphrase-multilingual-MiniLM-L12-v2 는 보통 384차원
    """
    if not sentences:
        raise ValueError("비교할 문장이 비어 있습니다.")
    return model.encode(sentences, convert_to_tensor=convert_to_tensor)


def pairwise_cosine_similarities(embeddings, query_index=0):
    """기준 문장(query)과 모든 문장 사이의 코사인 유사도를 계산합니다.

    코사인 유사도:
    - 두 벡터의 "방향"이 얼마나 비슷한지 측정 (-1 ~ 1, 보통 문장 임베딩은 0~1 근처)
    - 1에 가까울수록 의미가 비슷하다고 해석할 수 있음

    매개변수
    - embeddings  : encode_sentences 결과
    - query_index : 기준 문장의 인덱스 (기본 0 = 첫 문장)

    반환값
    - NumPy 배열 형태의 유사도 점수 (문장 개수만큼)
    """
    if query_index < 0 or query_index >= len(embeddings):
        raise IndexError(
            f"query_index={query_index} 는 범위를 벗어났습니다. "
            f"(문장 개수={len(embeddings)})"
        )

    # cos_sim(기준벡터, 전체벡터들) → shape (1, 문장개수)
    # .cpu()  : GPU에 있어도 CPU로 옮김
    # .numpy(): NumPy 배열로 변환
    # [0]     : (1, N) 에서 첫 행만 꺼내 (N,) 으로 만듦
    scores = cos_sim(embeddings[query_index], embeddings).cpu().numpy()[0]
    return scores


def print_similarity_report(sentences, scores, query_index=0, digits=3):
    """문장별 유사도를 초보자가 읽기 쉽게 출력합니다."""
    query = sentences[query_index]
    print(f"[기준 문장] ({query_index}) {query}")
    print("[코사인 유사도]")
    for i, (sentence, score) in enumerate(zip(sentences, scores)):
        mark = " ← 기준" if i == query_index else ""
        print(f"  ({i}) {score:.{digits}f} | {sentence}{mark}")
    print()
    print("관찰 포인트:")
    print("  - 자기 자신과의 유사도는 거의 1.0입니다.")
    print("  - 의미가 비슷한 문장일수록 점수가 높게 나오는 경향이 있습니다.")
    print("  - 유사도가 높다는 것은 '관련성 힌트'일 뿐,")
    print("    사실성·논리적 함의를 보장하지는 않습니다.")


def compare_sentences(
    sentences,
    model_name=DEFAULT_MODEL_NAME,
    query_index=0,
    digits=3,
):
    """문장들을 임베딩한 뒤, 기준 문장과의 유사도를 출력합니다.

    이 함수만 호출해도 전체 실습 흐름이 한 번에 실행됩니다.
    """
    print(f"모델 불러오는 중: {model_name}")
    model = load_model(model_name)

    embeddings = encode_sentences(model, sentences)
    print(f"임베딩 shape: {tuple(embeddings.shape)}  (문장수, 차원)")
    print()

    scores = pairwise_cosine_similarities(embeddings, query_index=query_index)
    print_similarity_report(sentences, scores, query_index=query_index, digits=digits)
    return scores


def read_sentences_from_input():
    """사용자에게 비교할 문장을 여러 줄로 입력받습니다.

    사용법:
    - 한 줄에 문장 하나씩 입력
    - 빈 줄을 입력하면 종료
    - 아무 것도 입력하지 않으면 기본 데모 문장을 사용
    """
    print("비교할 문장을 한 줄에 하나씩 입력하세요.")
    print("(빈 줄을 누르면 입력 종료 / 아무 것도 안 쓰면 기본 예제 사용)")
    lines = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        lines.append(line)
    return lines if lines else list(DEFAULT_SENTENCES)


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 미리 준비한 독일어 문장 3개 비교
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (독일어 문장 3개)")
    print("=" * 60)
    compare_sentences(DEFAULT_SENTENCES, query_index=0)
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 문장들로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 문장으로 비교하기")
    print("=" * 60)
    user_sentences = read_sentences_from_input()

    # 기준 문장 인덱스 (기본 0)
    query_text = input("기준 문장 번호(기본 0): ").strip()
    query_index = int(query_text) if query_text else 0

    print()
    compare_sentences(user_sentences, query_index=query_index)
