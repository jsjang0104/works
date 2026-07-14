"""
Training Dataset Generation for ME model
MT 모델(Helsinki)로 소스 문장을 번역하고 결과를 JSONL로 저장

원본 코드 출처 https://github.com/zouharvi/mt-metric-estimation
클로드의 도움을 받아 수정 후 실험 수행

====== 출력 형식 ======
    {"src": "...", "ref": "...", "tgts": [["hypothesis", score], ...]}

    - src   : 원문 (소스 언어 문장)
    - ref   : 참조 번역 (정답 번역, 데이터셋에서 가져옴)
    - tgts  : 빔 서치 가설 목록. 각 원소는 [번역문, log-prob score].
              score가 높을수록 모델이 자신있는 번역이며, 내림차순 정렬됨.

====== Experiment Setting ======

1. 번역 모델 변경
- 논문의 번역 모델: WMT19
- 실험 사용 모델: HelsinkiNLP
- 사유: WMT19가 python3.12와 호환이 안됨. 코랩 환경이라 기본 Python 버전을 바꾸기 쉽지 않음.
- 따라서 저자들이 제공한 mt_model_zoo.py에 있던 후보 MT 모델 중 하나인 HelsinkiNLP로 변경
- beam search 등 세부 디테일은 유지

2. 실험 환경
구글 colab A100 유료 컴퓨팅 단위 구입
파일 저장 경로가 google drive로 하드코딩 되어있음

3. 의존성
requirements.txt에 명시
"""

import torch
import datasets
import tqdm
import argparse
import os
import json

DEVICE = torch.device("cuda:0")


# 기존 논문에서는 WMT19 Transformer 사용
class HelsinkiWrap:
    def __init__(self, direction):
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        print("loading", f"Helsinki-NLP/opus-mt-{direction}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            f"Helsinki-NLP/opus-mt-{direction}"
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            f"Helsinki-NLP/opus-mt-{direction}"
        )
        self.model.eval()
        self.model.to(DEVICE)

    def translate(self, sent_src):
        return self.translate_batch([sent_src])[0]

    def translate_batch(self, sentences):
        inputs = self.tokenizer(
            sentences,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(DEVICE)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                num_beams=5,
                num_return_sequences=5,
                return_dict_in_generate=True,
                output_scores=True,
            )
        results = []
        for i in range(len(sentences)):
            hyps = []
            for j in range(5):
                idx = i * 5 + j
                trans = self.tokenizer.decode(
                    outputs.sequences[idx], skip_special_tokens=True
                )
                score = outputs.sequences_scores[idx].cpu().item()
                hyps.append([trans, score])
            results.append(sorted(hyps, key=lambda x: x[1], reverse=True))
        return results


MODELS = {
    "helsinki": lambda direction: HelsinkiWrap(direction),
}

# 언어 방향 → HuggingFace 데이터셋 이름 매핑.
# 양방향(예: en-de, de-en)이 동일 데이터셋을 공유한다.
# 원본에서는 여러 언어쌍을 사용 후 Appendix에 보고하였지만 본 실험에서는 영-독 언어쌍만 사용
DATASET_MAP = {
    "en-de": "wmt14",
}


def get_dataset(direction):
    """
    언어 방향에 해당하는 HuggingFace 학습 데이터셋을 로드한다.

    반환값의 각 원소는 {"translation": {src_lang: "...", tgt_lang: "..."}} 형태다.
    src/tgt 분리는 호출 측에서 방향(direction)을 파싱해 수행한다.

    Args:
        direction (str): 언어 방향 문자열 (예: "en-de", "zh-en")

    Returns:
        datasets.Dataset: HuggingFace Dataset 객체 (train split)
    """
    assert direction in DATASET_MAP, f"Unsupported direction: {direction}"
    return datasets.load_dataset("wmt14", "de-en")["train"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="/content/drive/MyDrive/en_de.jsonl")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("-ns", "--n-start", type=int, default=0)
    parser.add_argument("-ne", "--n-end", type=int, default=500)
    parser.add_argument("-m", "--model", default="helsinki")
    parser.add_argument("--direction", default="en-de")
    parser.add_argument("-bs", "--batch-size", type=int, default=8)
    parser.add_argument(
        "--dry-dataset", action="store_true", help="Only download the model & data"
    )
    parser.add_argument(
        "--dry-model", action="store_true", help="Only download the model"
    )
    return parser.parse_known_args()[0]


if __name__ == "__main__":
    args = parse_args()

    # 출력 파일이 이미 존재하고 --overwrite 플래그가 없으면 중단한다.
    # 실수로 기존 결과를 덮어쓰는 것을 방지한다.
    if os.path.exists(args.output) and not args.overwrite:
        print("The file", args.output, "already exists and you didn't --overwrite")
        print("Refusing to continue & exiting")
        exit()

    # 지정한 모델 키로 MT 모델 래퍼 인스턴스를 생성한다.
    model = MODELS[args.model](args.direction)

    # 모델이 정상 로드되었는지 간단한 번역으로 확인한다.
    print("Testing translate capabilities")
    print("hello?", model.translate("Hello"))

    # --dry-model: 모델 로드(및 다운로드)만 확인하고 종료
    if args.dry_model:
        exit("Exiting gracefully")

    # direction 문자열을 분리해 소스/타깃 언어 코드를 추출한다.
    # 예: "en-de" → src_lang="en", tgt_lang="de"
    langs = args.direction.split("-")
    src_lang = langs[0]
    tgt_lang = langs[1]

    # 데이터셋 로드 (HuggingFace datasets)
    data = get_dataset(args.direction)
    print("Total available", len(data))

    # --dry-dataset: 데이터셋 다운로드까지만 확인하고 종료
    if args.dry_dataset:
        exit("Exiting gracefully")

    all_sents = data[args.n_start * 1000 : args.n_end * 1000]["translation"]
    total = len(all_sents)
    bs = args.batch_size

    f = open(args.output, "w")

    for batch_start in tqdm.tqdm(range(0, total, bs), total=(total + bs - 1) // bs):
        batch = all_sents[batch_start : batch_start + bs]
        srcs = [s[src_lang] for s in batch]
        refs = [s[tgt_lang] for s in batch]

        tgts_batch = model.translate_batch(srcs)

        for src, ref, tgts in zip(srcs, refs, tgts_batch):
            f.write(
                json.dumps({"src": src, "ref": ref, "tgts": tgts}, ensure_ascii=False)
            )
            f.write("\n")

        if batch_start % (100 * bs) == 0:
            f.flush()

    f.close()
