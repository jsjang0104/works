"""09. Fine-tuning: 사전학습 모델의 분류 헤드 미세조정 뼈대

Pre-training(사전학습) vs Fine-tuning(미세조정)
- 사전학습: 위키·뉴스 등 대량 텍스트로 언어 지식을 먼저 익힘
            (08번의 MLM처럼, 가려진 단어를 맞추는 과제 등)
- 미세조정: 그 모델을 가져와, 우리 과제(여기서는 긍정/부정 분류)에 맞게
            마지막 분류 헤드와 가중치를 조금 더 학습시킴

주의:
- 실제 미세조정은 수천~수만 문장이 필요합니다.
- 이 파일은 "절차(파이프라인)"를 보여 주는 작은 데모입니다.

필요 패키지:
  pip install transformers datasets accelerate torch
"""

import os
import sys
from pathlib import Path


sys.stdout.reconfigure(encoding="utf-8")


def setup_windows_torch_dll():
    """Windows에서 torch DLL을 찾을 수 있도록 검색 경로를 보강합니다."""
    if sys.platform != "win32":
        return
    torch_lib = Path(sys.prefix) / "Lib" / "site-packages" / "torch" / "lib"
    if torch_lib.exists():
        os.add_dll_directory(str(torch_lib))
        os.environ["PATH"] = str(torch_lib) + os.pathsep + os.environ.get("PATH", "")


setup_windows_torch_dll()
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


# ------------------------------------------------------------
# 기본 설정값 (수업/실습용)
# ------------------------------------------------------------
# DistilBERT: BERT를 작게 증류한 모델. 수업 실습용으로 학습이 빠릅니다.
# 독일어로 사전학습된 버전(cased)을 사용합니다.
DEFAULT_MODEL_NAME = "distilbert-base-german-cased"
DEFAULT_OUTPUT_DIR = "finetuned_demo"
DEFAULT_MAX_LENGTH = 32
DEFAULT_EPOCHS = 1
DEFAULT_BATCH_SIZE = 2

# 아주 작은 독일어 감성 분류 데이터
#   label 1: 긍정(positiv),  label 0: 부정(negativ)
DEFAULT_ROWS = {
    "text": [
        "Der Kurs ist sehr gut.",
        "Der Kurs ist schlecht.",
        "Die Stunde war ausgezeichnet.",
        "Die Stunde war langweilig.",
    ],
    "label": [1, 0, 1, 0],
}


def build_dataset(rows=None, test_size=0.5, seed=42):
    """딕셔너리 형태의 데이터를 Hugging Face Dataset으로 만들고 분할합니다.

    매개변수
    - rows: {"text": [...], "label": [...]} 형식
    """
    if rows is None:
        rows = DEFAULT_ROWS
    if len(rows["text"]) != len(rows["label"]):
        raise ValueError("text 개수와 label 개수가 같아야 합니다.")
    if len(rows["text"]) < 2:
        raise ValueError("학습/평가 분할을 위해 문장이 2개 이상 필요합니다.")

    dataset = Dataset.from_dict(rows)
    return dataset.train_test_split(test_size=test_size, seed=seed)


def load_tokenizer_and_model(model_name=DEFAULT_MODEL_NAME, num_labels=2):
    """토크나이저와 분류용 모델을 불러옵니다.

    AutoModelForSequenceClassification:
    - 사전학습 가중치를 불러온 뒤, num_labels개 클래스용 분류 헤드를 붙입니다.
    - 헤드의 가중치는 아직 무작위 → 아래에서 미세조정으로 학습합니다.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
    )
    return tokenizer, model


def tokenize_dataset(dataset, tokenizer, max_length=DEFAULT_MAX_LENGTH):
    """문장 텍스트를 토큰 ID로 바꾸고, 학습용 텐서 형식으로 맞춥니다.

    - truncation=True        : 너무 긴 문장은 자름
    - padding='max_length'   : 짧은 문장은 max_length까지 패딩해 배치 길이를 맞춤
    - remove_columns('text') : 원문 열은 학습에 필요 없으므로 제거
    """

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
        )

    return (
        dataset.map(tokenize, batched=True)
        .remove_columns("text")
        .with_format("torch")
    )


def make_training_args(
    output_dir=DEFAULT_OUTPUT_DIR,
    num_train_epochs=DEFAULT_EPOCHS,
    per_device_train_batch_size=DEFAULT_BATCH_SIZE,
):
    """실습용 TrainingArguments를 만듭니다.

    report_to='none': wandb 등 외부 로깅을 끄고 콘솔만 사용합니다.
    """
    return TrainingArguments(
        output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_train_batch_size,
        report_to="none",
    )


def run_finetuning(
    rows=None,
    model_name=DEFAULT_MODEL_NAME,
    output_dir=DEFAULT_OUTPUT_DIR,
    max_length=DEFAULT_MAX_LENGTH,
    num_train_epochs=DEFAULT_EPOCHS,
    batch_size=DEFAULT_BATCH_SIZE,
):
    """데이터 준비 → 토큰화 → Trainer 학습까지 한 번에 실행합니다.

    이 함수만 호출해도 전체 실습 흐름이 실행됩니다.
    """
    print(f"모델 불러오는 중: {model_name}")
    tokenizer, model = load_tokenizer_and_model(model_name)

    print("데이터셋 준비 중...")
    split = build_dataset(rows=rows)
    print(f"  train 개수: {len(split['train'])}, test 개수: {len(split['test'])}")

    split = tokenize_dataset(split, tokenizer, max_length=max_length)

    args = make_training_args(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
    )

    # Trainer가 순전파 → 손실 → 역전파 → 가중치 갱신을 한 번에 수행합니다.
    print("미세조정 시작...")
    trainer = Trainer(model=model, args=args, train_dataset=split["train"])
    train_result = trainer.train()

    print()
    print("관찰 포인트:")
    print("  - 사전학습 모델 + 작은 분류 헤드를 과제에 맞게 추가로 학습합니다.")
    print("  - 데이터가 매우 작아 성능보다 '절차 이해'가 목적입니다.")
    print(f"  - 학습 결과는 '{output_dir}' 폴더에 저장됩니다.")
    return trainer, train_result


def read_labeled_rows():
    """사용자에게 (문장, 라벨)을 입력받습니다.

    형식: 문장|0 또는 문장|1
    빈 줄이면 종료. 아무 것도 없으면 기본 예제를 사용합니다.
    """
    print("학습 문장을 '문장|라벨' 형식으로 입력하세요. (라벨: 1=긍정, 0=부정)")
    print("예: Der Kurs ist gut.|1")
    print("(빈 줄을 누르면 입력 종료 / 아무 것도 안 쓰면 기본 예제 사용)")

    texts = []
    labels = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        if "|" not in line:
            print("  형식 오류: 문장|0 또는 문장|1 로 입력하세요.")
            continue
        text, label_str = line.rsplit("|", 1)
        text = text.strip()
        try:
            label = int(label_str.strip())
        except ValueError:
            print("  라벨은 0 또는 1 정수여야 합니다.")
            continue
        if label not in (0, 1):
            print("  라벨은 0 또는 1이어야 합니다.")
            continue
        texts.append(text)
        labels.append(label)

    if not texts:
        return dict(DEFAULT_ROWS)
    return {"text": texts, "label": labels}


if __name__ == "__main__":
    # --------------------------------------------------
    # A. 기본 데모: 미리 준비한 4문장으로 미세조정 절차 체험
    # --------------------------------------------------
    print("=" * 60)
    print("A. 기본 데모 (독일어 감성 분류 4문장)")
    print("=" * 60)
    run_finetuning()
    print()

    # --------------------------------------------------
    # B. 일반화: 사용자가 입력한 문장으로 같은 절차 반복
    # --------------------------------------------------
    print("=" * 60)
    print("B. 직접 입력한 데이터로 미세조정하기")
    print("=" * 60)
    user_rows = read_labeled_rows()
    print()
    run_finetuning(rows=user_rows, output_dir="finetuned_demo_user")
