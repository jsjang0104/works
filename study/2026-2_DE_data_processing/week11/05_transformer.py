"""05. Transformer: 토큰화·위치 정보·출력 형태 관찰

Transformer란?
- RNN처럼 단어를 "한 칸씩 순서대로" 처리하지 않습니다.
- Attention으로 문장 안 모든 토큰 사이의 관계를 "한꺼번에(병렬로)" 계산합니다.
- 같은 단어도 주변 문맥에 따라 다른 벡터가 됩니다. (= 문맥 임베딩)

이 실습에서 보는 것:
1) 문장 → 서브워드 토큰 → 정수 ID
2) 위치(position) 정보가 왜 필요한지
3) 모델 출력의 형태
   - last_hidden_state : 토큰별 문맥 벡터
   - pooler_output     : [CLS]를 가공한 문장 대표 벡터

필요 패키지:
  pip install torch transformers
"""

import torch
from transformers import AutoTokenizer, AutoModel


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
# bert-base-german-cased:
#   - 독일어용 BERT (encoder 전용 Transformer)
#   - cased = 대소문자를 구분함 (Der ≠ der)
# 처음 실행 시 모델 가중치를 인터넷에서 다운로드합니다.
DEFAULT_MODEL_NAME = "bert-base-german-cased"

# 기본 데모 문장
DEFAULT_SENTENCES = [
    "Der kleine Hund läuft im Park.",  # 작은 개가 공원에서 달린다
]


def load_tokenizer_and_model(model_name=DEFAULT_MODEL_NAME):
    """모델 이름으로 토크나이저와 Transformer 본체를 불러옵니다.

    AutoTokenizer / AutoModel:
    - 모델 이름만 주면, 그 모델에 맞는 클래스를 자동으로 골라 줍니다.
    - tokenizer : 문장 → 토큰 → 정수 ID
    - model     : ID를 받아 각 토큰의 문맥 벡터를 계산
                  (여기서는 분류용 헤드 없이 본체만 사용)

    반환값
    - (tokenizer, model)
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model


def tokenize_sentence(tokenizer, sentence, return_tensors="pt"):
    """한 문장을 모델 입력 형식(텐서 딕셔너리)으로 변환합니다.

    주요 키:
    - input_ids      : 토큰의 정수 ID 열
    - attention_mask : 실제 토큰=1, 패딩=0
                       (문장 하나면 보통 패딩이 없어 전부 1)
    - token_type_ids : 문장 A/B 구분용 (단일 문장에서는 보통 전부 0)

    return_tensors="pt" 이면 PyTorch 텐서로 반환합니다.
    """
    if not sentence or not str(sentence).strip():
        raise ValueError("문장이 비어 있습니다.")
    return tokenizer(sentence, return_tensors=return_tensors)


def get_tokens(tokenizer, input_ids):
    """정수 ID 열을 사람이 읽을 수 있는 토큰 문자열 목록으로 되돌립니다.

    BERT는 WordPiece 토큰화를 사용합니다.
    - 긴 단어/희귀 단어는 여러 조각으로 쪼개질 수 있습니다.
    - 특수 토큰:
        [CLS] : 문장 앞에 붙는 분류용 자리 (문장 전체를 대표하는 자리)
        [SEP] : 문장 끝에 붙는 구분 토큰
    """
    # input_ids 가 (배치, 길이) 형태면 첫 문장만 사용
    ids = input_ids[0] if hasattr(input_ids, "dim") and input_ids.dim() == 2 else input_ids
    return tokenizer.convert_ids_to_tokens(ids)


def get_position_ids(sequence_length):
    """위치 ID 예시 목록을 만듭니다. (0, 1, 2, ..., 길이-1)

    Transformer는 토큰 '순서(위치)'를 스스로 알지 못합니다.
    그래서 위치 임베딩(position embedding)을 더해 줍니다.
    여기서는 개념 이해를 위해 자리 번호만 출력합니다.
    """
    return list(range(sequence_length))


def run_model(model, inputs):
    """토크나이저 출력을 Transformer에 넣어 추론합니다.

    torch.no_grad():
    - 기울기(gradient)를 계산하지 않음
    - 학습이 아니라 '관찰/추론'만 할 때 메모리·속도에 유리합니다.

    model(**inputs):
    - tokenizer가 만든 딕셔너리를 키워드 인자로 그대로 전달
    """
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs


def print_transformer_report(tokenizer, inputs, outputs):
    """토큰화 결과와 모델 출력 형태를 초보자가 읽기 쉽게 출력합니다."""
    input_ids = inputs["input_ids"]
    tokens = get_tokens(tokenizer, input_ids)
    seq_len = input_ids.shape[1]

    print("[입력 문장 토큰화]")
    print(f"  토큰: {tokens}")
    print(f"  input_ids 형태: {tuple(input_ids.shape)}  (배치크기, 시퀀스길이)")
    print(f"  position_ids 예시: {get_position_ids(seq_len)}")
    print()

    # last_hidden_state: 마지막 Transformer 층의 토큰별 문맥 벡터
    #   형태 예: (1, 시퀀스 길이, 768)
    #   768 = BERT-base의 은닉 차원
    print("[모델 출력]")
    print(
        f"  토큰별 문맥 표현(last_hidden_state) 형태: "
        f"{tuple(outputs.last_hidden_state.shape)}"
    )

    # pooler_output: [CLS] 벡터를 한 번 더 변환한 문장 대표 벡터
    #   형태 예: (1, 768) → 문장 하나당 벡터 하나
    # 주의:
    #   pooler는 다음 문장 예측(NSP)용으로 학습된 경우가 많아,
    #   문장 의미 비교에는 04의 Sentence Transformer가 더 적합합니다.
    if getattr(outputs, "pooler_output", None) is not None:
        print(
            f"  문장 대표 표현(pooler_output) 형태: "
            f"{tuple(outputs.pooler_output.shape)}"
        )
    else:
        print("  문장 대표 표현(pooler_output): 이 모델에는 없습니다.")

    print()
    print("관찰 포인트:")
    print("  - 토큰 목록 맨 앞/뒤에 [CLS], [SEP]가 붙습니다.")
    print("  - last_hidden_state 의 두 번째 축 길이는 토큰 개수와 같습니다.")
    print("  - 같은 단어도 문맥에 따라 다른 벡터가 됩니다.")
    print("  - 문장 유사도 비교가 목적이면 Sentence Embedding(04)을 쓰세요.")



def inspect_sentence(sentence, model_name=DEFAULT_MODEL_NAME):
    """한 문장에 대해 토큰화 → 모델 추론 → 결과 출력을 한 번에 실행합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.

    반환값
    - (inputs, outputs) 튜플
    """
    print(f"모델 불러오는 중: {model_name}")
    tokenizer, model = load_tokenizer_and_model(model_name)

    inputs = tokenize_sentence(tokenizer, sentence)
    outputs = run_model(model, inputs)

    print(f"문장: {sentence}")
    print()
    print_transformer_report(tokenizer, inputs, outputs)
    return inputs, outputs


def inspect_sentences(sentences, model_name=DEFAULT_MODEL_NAME):
    """여러 문장을 순서대로 관찰합니다. (모델은 한 번만 로드)

    매개변수
    - sentences : 문자열 목록
    - model_name: Hugging Face 모델 이름

    반환값
    - [(inputs, outputs), ...] 목록
    """
    if not sentences:
        raise ValueError("관찰할 문장이 비어 있습니다.")

    print(f"모델 불러오는 중: {model_name}")
    tokenizer, model = load_tokenizer_and_model(model_name)
    results = []

    for i, sentence in enumerate(sentences):
        print("-" * 60)
        print(f"[{i}] {sentence}")
        print("-" * 60)
        inputs = tokenize_sentence(tokenizer, sentence)
        outputs = run_model(model, inputs)
        print_transformer_report(tokenizer, inputs, outputs)
        results.append((inputs, outputs))

    return results


def read_sentences_from_input():
    """사용자에게 관찰할 문장을 여러 줄로 입력받습니다.

    사용법:
    - 한 줄에 문장 하나씩 입력
    - 빈 줄을 입력하면 종료
    - 아무 것도 입력하지 않으면 기본 데모 문장을 사용
    """
    print("관찰할 문장을 한 줄에 하나씩 입력하세요.")
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
    # A. 기본 데모: 미리 준비한 독일어 문장 1개 관찰
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (독일어 문장 1개)")
    print("=" * 60)
    inspect_sentences(DEFAULT_SENTENCES)
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 문장들로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 문장으로 관찰하기")
    print("=" * 60)
    user_sentences = read_sentences_from_input()
    print()
    inspect_sentences(user_sentences)
