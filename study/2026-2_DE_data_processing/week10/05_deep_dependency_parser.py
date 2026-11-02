"""딥러닝으로 독일어 문장의 의존 문법을 분석하는 실습

의존 문법이란:
- 문장을 덩어리(NP, VP)로 묶지 않고, 단어와 단어를 화살표로 연결합니다.
- 화살표가 출발하는 단어 = 의존소(dependent, 꾸밈을 받거나 지배를 받는 쪽)
- 화살표가 도착하는 단어 = 지배소(head, 문법을 이끄는 쪽)
- 화살표 이름 = 의존 관계 (주어 nsubj, 목적어 obj, 관사 det ...)

예: Der Hund schläft.
    Der  --det-->  Hund  --nsubj-->  schläft  --root-->  ROOT

    풀이: 관사 Der가 명사 Hund를 한정하고,
          Hund가 동사 schläft의 주어이며,
          schläft가 문장 전체의 중심(뿌리)입니다.

이 실습의 아이디어:
- 독일어 어순 규칙을 직접 쓰지 않습니다.
- 각 단어마다 두 가지를 예측합니다.
  1) 내 지배소는 몇 칸 옆에 있는가? (상대 위치, 오프셋)
  2) 그 관계는 무엇인가? (nsubj, obj, det ...)
- 04강과 같이 단어를 작은 벡터(임베딩)로 바꾼 뒤,
  주변 단어를 보는 다층 신경망이 위 두 값을 찾습니다.

실제 분석기는 훨씬 큰 말뭉치와 양방향 LSTM·트랜스포머를 씁니다.
여기서는 "신경망이 단어 패턴으로 의존 구조를 배운다"는 장면만 봅니다.
"""

# numpy: 숫자 벡터·행렬 계산
# torch: 딥러닝 계산 (단어 임베딩 + 신경망)
# matplotlib: 의존 화살표를 문장 위에 그리기
# accuracy_score: 정답과 예측이 얼마나 맞는지 비율로 계산
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Patch
from sklearn.metrics import accuracy_score

# Windows에서 그래프 한글이 깨지지 않도록 글꼴을 지정합니다.
plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)

# 실행할 때마다 같은 결과가 나오도록 난수를 고정합니다.
np.random.seed(42)
torch.manual_seed(42)


# ---------------------------------------------------------------------------
# 1) 작은 정답 데이터
#    실제 의존 분석기는 Universal Dependencies 같은 말뭉치(수만 문장)를 쓰지만,
#    여기서는 짧은 독일어 문장으로 "주어·목적어·관사 연결을 배운다"는 연습만 합니다.
#
#    각 항목: (단어 목록, 지배소 번호 목록, 관계 이름 목록)
#    지배소 번호는 CoNLL 방식입니다.
#      0 = 문장의 뿌리(ROOT)
#      1 이상 = 그 번호의 단어가 지배소 (첫 단어가 1번)
# ---------------------------------------------------------------------------
SENTENCES = [
    # 자동사: 관사 + 명사(주어) + 동사
    (["Der", "Hund", "schläft", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Die", "Katze", "schläft", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Das", "Kind", "schläft", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Der", "Student", "liest", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Die", "Lehrerin", "spricht", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Das", "Kind", "lacht", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Die", "Kinder", "spielen", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Der", "Mann", "trinkt", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Die", "Frau", "kauft", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    # 타동사: 주어 + 동사 + 목적어
    (["Der", "Hund", "jagt", "die", "Katze", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Die", "Katze", "jagt", "die", "Maus", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Der", "Student", "liest", "ein", "Buch", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Die", "Lehrerin", "erklärt", "die", "Übung", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Die", "Frau", "kauft", "Brot", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "obj", "punct"]),
    (["Der", "Mann", "trinkt", "Kaffee", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "obj", "punct"]),
    (["Ein", "Kind", "schreibt", "einen", "Brief", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Die", "Lehrerin", "lobt", "den", "Studenten", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Der", "Hund", "jagt", "den", "Mann", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Die", "Kinder", "lesen", "ein", "Buch", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    # 형용사가 명사를 수식 (amod)
    (["Kleine", "Kinder", "spielen", "."],
     [2, 3, 0, 3],
     ["amod", "nsubj", "root", "punct"]),
    (["Der", "alte", "Mann", "trinkt", "Kaffee", "."],
     [3, 3, 4, 0, 4, 4],
     ["det", "amod", "nsubj", "root", "obj", "punct"]),
    (["Die", "junge", "Frau", "kauft", "Brot", "."],
     [3, 3, 4, 0, 4, 4],
     ["det", "amod", "nsubj", "root", "obj", "punct"]),
    (["Das", "kleine", "Kind", "lacht", "."],
     [3, 3, 4, 0, 4],
     ["det", "amod", "nsubj", "root", "punct"]),
    (["Der", "junge", "Student", "liest", "."],
     [3, 3, 4, 0, 4],
     ["det", "amod", "nsubj", "root", "punct"]),
    # 부사 (advmod), 부정어 nicht 도 부사로 봅니다.
    (["Der", "Hund", "schläft", "gern", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "advmod", "punct"]),
    (["Die", "Kinder", "spielen", "heute", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "advmod", "punct"]),
    (["Der", "Student", "liest", "langsam", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "advmod", "punct"]),
    (["Die", "Katze", "schläft", "nicht", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "advmod", "punct"]),
    # 전치사구: 전치사(case)가 명사를 표시하고, 그 명사가 동사의 상황어(obl)
    (["Die", "Kinder", "spielen", "im", "Garten", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "case", "obl", "punct"]),
    (["Der", "Hund", "schläft", "im", "Haus", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "case", "obl", "punct"]),
    (["Die", "Katze", "sitzt", "auf", "dem", "Tisch", "."],
     [2, 3, 0, 6, 6, 3, 3],
     ["det", "nsubj", "root", "case", "det", "obl", "punct"]),
    (["Der", "Student", "liest", "in", "der", "Bibliothek", "."],
     [2, 3, 0, 6, 6, 3, 3],
     ["det", "nsubj", "root", "case", "det", "obl", "punct"]),
    (["Das", "Kind", "spielt", "im", "Garten", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "case", "obl", "punct"]),
    # 완료 시제: 조동사 haben + 과거분사
    # UD에서는 본동사(과거분사)가 root, hat 이 aux 입니다.
    (["Der", "Student", "hat", "ein", "Buch", "gelesen", "."],
     [2, 6, 6, 5, 6, 0, 6],
     ["det", "nsubj", "aux", "det", "obj", "root", "punct"]),
    (["Die", "Lehrerin", "hat", "die", "Übung", "erklärt", "."],
     [2, 6, 6, 5, 6, 0, 6],
     ["det", "nsubj", "aux", "det", "obj", "root", "punct"]),
    (["Das", "Kind", "hat", "Brot", "gekauft", "."],
     [2, 5, 5, 5, 0, 5],
     ["det", "nsubj", "aux", "obj", "root", "punct"]),
    (["Der", "Mann", "hat", "Kaffee", "getrunken", "."],
     [2, 5, 5, 5, 0, 5],
     ["det", "nsubj", "aux", "obj", "root", "punct"]),
    # 계사 ist: 형용사가 root, ist 는 cop
    (["Die", "Blume", "ist", "schön", "."],
     [2, 4, 4, 0, 4],
     ["det", "nsubj", "cop", "root", "punct"]),
    (["Das", "Wetter", "ist", "kalt", "."],
     [2, 4, 4, 0, 4],
     ["det", "nsubj", "cop", "root", "punct"]),
    (["Der", "Hund", "ist", "alt", "."],
     [2, 4, 4, 0, 4],
     ["det", "nsubj", "cop", "root", "punct"]),
    (["Die", "Übung", "ist", "leicht", "."],
     [2, 4, 4, 0, 4],
     ["det", "nsubj", "cop", "root", "punct"]),
]

# 화면에 한글로 보여 줄 의존 관계 이름
REL_KO = {
    "root": "뿌리",
    "nsubj": "주어",
    "obj": "목적어",
    "det": "한정사",
    "amod": "형용사수식",
    "advmod": "부사수식",
    "case": "전치사",
    "obl": "상황어",
    "aux": "조동사",
    "cop": "계사",
    "punct": "문장부호",
}

# 단어 창의 반지름. 3이면 왼쪽 3단어 + 자기 자신 + 오른쪽 3단어 = 7단어를 봅니다.
# 짧은 문장에서는 문장 거의 전체가 창 안에 들어옵니다.
WINDOW = 3
PAD = "<PAD>"     # 문장 맨 앞·뒤에 칸이 모자랄 때 채우는 빈 칸
UNK = "<UNK>"     # 학습 때 본 적 없는 단어
ROOT_TOK = "<ROOT>"  # 뿌리(문장 밖 가상 마디)를 가리킬 때 쓰는 특수 단어


def check_sentences(sentences):
    """번호가 범위를 벗어나지 않는지, 뿌리가 하나인지, 자기 자신을 가리키지 않는지 검사합니다."""
    for tokens, heads, rels in sentences:
        n = len(tokens)
        if not (n == len(heads) == len(rels)):
            raise ValueError(f"길이가 다릅니다: {tokens}")
        roots = [i for i, h in enumerate(heads) if h == 0]
        if len(roots) != 1:
            raise ValueError(f"뿌리가 하나가 아닙니다: {tokens}")
        if rels[roots[0]] != "root":
            raise ValueError(f"뿌리 단어의 관계 이름이 root가 아닙니다: {tokens}")
        for i, h in enumerate(heads):
            if h == i + 1:
                raise ValueError(f"자기 자신을 지배소로 가리킵니다: {tokens[i]}")
            if h < 0 or h > n:
                raise ValueError(f"지배소 번호가 범위를 벗어납니다: {tokens}")


def head_to_offset(index, head):
    """단어 위치(0부터)와 지배소 번호(1부터, 0=ROOT)를 상대 위치 글자로 바꿉니다.

    예: 0번째 Der 의 지배소가 2(Hund)이면 오프셋은 +1
        2번째 schläft 의 지배소가 0이면 오프셋은 ROOT
    """
    if head == 0:
        return "ROOT"
    return str((head - 1) - index)


def offset_to_head(index, offset, n_tokens):
    """예측한 오프셋을 다시 지배소 번호로 바꿉니다. 범위를 벗어나면 ROOT(0)로 둡니다."""
    if offset == "ROOT":
        return 0
    head_index = index + int(offset)
    if head_index < 0 or head_index >= n_tokens or head_index == index:
        return 0
    return head_index + 1


# ---------------------------------------------------------------------------
# 2) 각 단어를 주변 단어 창으로 표현하기
#
#    04강: 글자 하나 + 양쪽 글자 → 형태소 태그
#    05강: 단어 하나 + 양쪽 단어 → 지배소 위치 + 관계 이름
#
#    창이 필요한 이유:
#    'Die'만 보면 주어의 관사인지 목적어의 관사인지 알 수 없습니다.
#    오른쪽이 Hund schläft 이면 주어 쪽, jagt die Katze 이면 목적어 쪽일 가능성이 큽니다.
# ---------------------------------------------------------------------------
def word_window(tokens, index, window=WINDOW):
    """한 단어를 판단할 때 함께 볼 주변 단어 목록을 만듭니다.

    예: ['Der', 'Hund', 'schläft', '.'] 의 0번째 'Der'
        → ['<PAD>', '<PAD>', '<PAD>', 'Der', 'Hund', 'schläft', '.']
    """
    words = []
    for offset in range(-window, window + 1):
        j = index + offset
        if 0 <= j < len(tokens):
            words.append(tokens[j])
        else:
            words.append(PAD)
    return words


def build_word_vocab(token_lists):
    """학습 문장에 나온 단어 + PAD/UNK/ROOT 를 번호로 매깁니다.

    신경망은 글자열을 받지 못하고 숫자만 받습니다.
    그래서 Hund→7, schläft→18 처럼 변환표가 필요합니다.
    """
    vocab = set()
    for tokens in token_lists:
        vocab.update(tokens)
    symbols = [PAD, UNK, ROOT_TOK] + sorted(vocab)
    return {w: i for i, w in enumerate(symbols)}


def window_to_ids(window_words, word_to_id):
    """단어 창을 번호 목록으로 바꿉니다. 모르는 단어는 UNK 번호를 씁니다."""
    unk = word_to_id[UNK]
    return [word_to_id.get(w, unk) for w in window_words]


def word_id(token, word_to_id):
    """한 단어의 번호를 돌려줍니다. 없으면 UNK입니다."""
    return word_to_id.get(token, word_to_id[UNK])


def make_dataset(sentences, word_to_id, offset_to_id, rel_to_id):
    """모든 문장의 모든 단어를 학습 한 줄로 펼칩니다.

    한 문장이 4단어이면 샘플이 4개 생깁니다.
    각 줄에는
      - 주변 단어 창 번호 (지배소 위치를 맞힐 때 사용)
      - 정답 오프셋 번호
      - 의존소 단어 번호, 지배소 단어 번호 (관계 이름을 맞힐 때 사용)
      - 정답 관계 번호
    가 들어갑니다.
    """
    windows, y_off, dep_ids, head_ids, y_rel = [], [], [], [], []
    for tokens, heads, rels in sentences:
        for i, token in enumerate(tokens):
            windows.append(window_to_ids(word_window(tokens, i), word_to_id))
            y_off.append(offset_to_id[head_to_offset(i, heads[i])])
            dep_ids.append(word_id(token, word_to_id))
            if heads[i] == 0:
                head_ids.append(word_to_id[ROOT_TOK])
            else:
                head_ids.append(word_id(tokens[heads[i] - 1], word_to_id))
            y_rel.append(rel_to_id[rels[i]])
    return (
        np.array(windows, dtype=np.int64),
        np.array(y_off, dtype=np.int64),
        np.array(dep_ids, dtype=np.int64),
        np.array(head_ids, dtype=np.int64),
        np.array(y_rel, dtype=np.int64),
    )


# ---------------------------------------------------------------------------
# 3) 데이터 준비: 문장 단위로 학습/시험 분리
#
#    단어 단위로 나누면 같은 문장의 단어가 학습과 시험에 섞입니다.
#    그러면 "처음 보는 문장"을 시험하는 것이 아니므로, 문장을 먼저 나눕니다.
#
#    시험 문장은 통째로 학습에 넣지 않되, 단어와 패턴은 다른 문장에서
#    이미 본 조합으로 고릅니다. 신경망이 구조를 옮겨 쓰는지 보기 위해서입니다.
#    예: 학습에 Die Katze schläft,  ... jagt die Maus
#        → 시험의 Die Maus schläft 를 주어-동사로 연결할 수 있는지
# ---------------------------------------------------------------------------
check_sentences(SENTENCES)

# 학습에는 SENTENCES만 넣고, 시험 문장은 아래에 따로 둡니다.
# 시험 문장의 단어·패턴은 학습에 나오되, 그 조합(문장 전체)은 처음 보는 것입니다.
train_sents = SENTENCES
TEST_SENTS = [
    (["Die", "Maus", "schläft", "."],
     [2, 3, 0, 3],
     ["det", "nsubj", "root", "punct"]),
    (["Der", "Mann", "liest", "ein", "Buch", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "det", "obj", "punct"]),
    (["Das", "kleine", "Kind", "spielt", "."],
     [3, 3, 4, 0, 4],
     ["det", "amod", "nsubj", "root", "punct"]),
    (["Die", "Katze", "schläft", "gern", "."],
     [2, 3, 0, 3, 3],
     ["det", "nsubj", "root", "advmod", "punct"]),
    (["Der", "Hund", "sitzt", "im", "Garten", "."],
     [2, 3, 0, 5, 3, 3],
     ["det", "nsubj", "root", "case", "obl", "punct"]),
    (["Die", "Frau", "hat", "ein", "Buch", "gelesen", "."],
     [2, 6, 6, 5, 6, 0, 6],
     ["det", "nsubj", "aux", "det", "obj", "root", "punct"]),
    (["Der", "alte", "Hund", "schläft", "."],
     [3, 3, 4, 0, 4],
     ["det", "amod", "nsubj", "root", "punct"]),
    (["Die", "Übung", "ist", "schön", "."],
     [2, 4, 4, 0, 4],
     ["det", "nsubj", "cop", "root", "punct"]),
]
check_sentences(TEST_SENTS)
test_sents = TEST_SENTS

# 변환표는 학습 문장의 단어만으로 만듭니다.
word_to_id = build_word_vocab([s[0] for s in train_sents])

# 오프셋·관계 이름도 번호로 바꿉니다. 신경망의 출력 칸 하나가 종류 하나에 해당합니다.
offset_names = sorted({head_to_offset(i, h) for tokens, heads, _ in train_sents for i, h in enumerate(heads)})
# 시험 문장에만 있는 오프셋이 빠져 예측을 못 하는 일을 막기 위해, 가까운 칸을 미리 넣습니다.
for extra in ["-5", "-4", "-3", "-2", "-1", "1", "2", "3", "4", "5", "ROOT"]:
    if extra not in offset_names:
        offset_names.append(extra)
offset_names = sorted(offset_names, key=lambda x: (x != "ROOT", int(x) if x != "ROOT" else 0))
rel_names = sorted({r for _t, _h, rels in train_sents for r in rels})
offset_to_id = {name: i for i, name in enumerate(offset_names)}
id_to_offset = {i: name for name, i in offset_to_id.items()}
rel_to_id = {name: i for i, name in enumerate(rel_names)}
id_to_rel = {i: name for name, i in rel_to_id.items()}

X_win, y_off, dep_ids, head_ids, y_rel = make_dataset(
    train_sents, word_to_id, offset_to_id, rel_to_id
)

print("학습 문장 수:", len(train_sents), "/ 시험 문장 수:", len(test_sents))
print("단어 종류 수(PAD/UNK/ROOT 포함):", len(word_to_id))
print("오프셋 종류:", ", ".join(offset_names))
print("관계 종류:", ", ".join(rel_names))
print("학습 단어 샘플 수:", len(y_off))
print()


# ---------------------------------------------------------------------------
# 4) 의존 분석 신경망
#
#    02강 벡터: 사람이 횟수를 세어 만든 값
#    여기 임베딩: 학습이 스스로 찾는 작은 단어 벡터
#                 같은 역할의 단어(관사 Der/Die/Das, 동사 schläft/liest)가
#                 비슷한 숫자를 갖게 됩니다.
#
#    두 갈래 출력 (한 은닉 표현을 공유하지 않고, 역할에 맞게 나눕니다):
#      갈래 A) 단어 창 → 지배소가 몇 칸 옆인지
#      갈래 B) 의존소 단어 + 지배소 단어 → 관계 이름
#    실제 분석기도 "누구와 연결되는가"와 "연결의 이름은 무엇인가"를 나누어 학습합니다.
# ---------------------------------------------------------------------------
class DepParser(nn.Module):
    """주변 단어를 보고 지배소 위치와 관계 이름을 예측하는 작은 신경망입니다."""

    def __init__(self, vocab_size, n_offsets, n_rels, emb_dim=24, hidden=64, window_size=2 * WINDOW + 1):
        super().__init__()
        # 단어 번호 → 길이 24짜리 벡터. 이 숫자들은 학습하면서 바뀝니다.
        self.emb = nn.Embedding(vocab_size, emb_dim)
        # 창이 7단어이면 7 * 24 = 168차원이 은닉층으로 들어갑니다.
        self.head_hidden = nn.Linear(emb_dim * window_size, hidden)
        self.head_out = nn.Linear(hidden, n_offsets)
        # 의존소 벡터와 지배소 벡터를 이어 붙여 관계를 맞힙니다. 24 + 24 = 48차원.
        self.rel_hidden = nn.Linear(emb_dim * 2, hidden)
        self.rel_out = nn.Linear(hidden, n_rels)

    def score_heads(self, window_ids):
        # window_ids 모양: (샘플 수, 창 길이)
        vectors = self.emb(window_ids)
        flat = vectors.reshape(window_ids.size(0), -1)
        hidden = torch.relu(self.head_hidden(flat))
        return self.head_out(hidden)

    def score_rels(self, dep_word_ids, head_word_ids):
        # 두 단어를 각각 임베딩한 뒤 한 줄로 이어 붙입니다.
        dep_vec = self.emb(dep_word_ids)
        head_vec = self.emb(head_word_ids)
        pair = torch.cat([dep_vec, head_vec], dim=1)
        hidden = torch.relu(self.rel_hidden(pair))
        return self.rel_out(hidden)


parser = DepParser(
    vocab_size=len(word_to_id),
    n_offsets=len(offset_names),
    n_rels=len(rel_names),
)

# 텐서: 파이토치가 기울기(얼마나 고칠지)를 계산할 수 있는 숫자 묶음
X_win_t = torch.tensor(X_win)
y_off_t = torch.tensor(y_off)
dep_t = torch.tensor(dep_ids)
head_t = torch.tensor(head_ids)
y_rel_t = torch.tensor(y_rel)

# CrossEntropyLoss: 정답 칸의 점수는 높이고, 다른 칸의 점수는 낮추도록 차이를 재는 함수
# Adam: 그 차이를 줄이는 방향으로 가중치를 조금씩 수정하는 최적화 방법
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(parser.parameters(), lr=0.01)

n_epochs = 160
for epoch in range(1, n_epochs + 1):
    parser.train()
    head_scores = parser.score_heads(X_win_t)
    rel_scores = parser.score_rels(dep_t, head_t)
    # 두 과제를 더해 한 번에 학습합니다. 어느 한쪽만 잘하게 치우치는 것을 줄입니다.
    loss = loss_fn(head_scores, y_off_t) + loss_fn(rel_scores, y_rel_t)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if epoch in (1, 40, 80, 120, 160):
        print(f"학습 {epoch:3d}번째, 손실(작을수록 좋음): {loss.item():.3f}")


def predict_sentence(tokens):
    """한 문장의 각 단어에 대해 (지배소 번호, 관계 이름)을 예측합니다.

    순서:
    1) 창을 보고 오프셋을 고른다
    2) 오프셋을 지배소 번호로 바꾼다
    3) 의존소 단어와 (예측된) 지배소 단어를 보고 관계 이름을 고른다
    """
    parser.eval()
    n = len(tokens)
    windows = np.array(
        [window_to_ids(word_window(tokens, i), word_to_id) for i in range(n)],
        dtype=np.int64,
    )
    dep = np.array([word_id(tok, word_to_id) for tok in tokens], dtype=np.int64)

    with torch.no_grad():  # 예측만 할 때는 수정량 계산이 필요 없습니다.
        off_ids = parser.score_heads(torch.tensor(windows)).argmax(dim=1).numpy()

    heads = []
    head_word_ids = []
    for i, off_id in enumerate(off_ids):
        offset = id_to_offset[int(off_id)]
        head = offset_to_head(i, offset, n)
        heads.append(head)
        if head == 0:
            head_word_ids.append(word_to_id[ROOT_TOK])
        else:
            head_word_ids.append(word_id(tokens[head - 1], word_to_id))

    with torch.no_grad():
        rel_ids = parser.score_rels(torch.tensor(dep), torch.tensor(head_word_ids)).argmax(dim=1).numpy()
    rels = [id_to_rel[int(i)] for i in rel_ids]
    return heads, rels


# ---------------------------------------------------------------------------
# 5) 평가: UAS 와 LAS
#
#    UAS (Unlabeled Attachment Score): 지배소만 맞으면 정답
#    LAS (Labeled Attachment Score): 지배소와 관계 이름을 모두 맞혀야 정답
#
#    의존 분석에서 가장 흔히 쓰는 두 숫자입니다.
#    문장부호는 맞히기 쉬우므로, 문장부호를 뺀 값도 함께 보여 줍니다.
# ---------------------------------------------------------------------------
def collect_eval(sentences):
    gold_heads, pred_heads, gold_rels, pred_rels, is_punct = [], [], [], [], []
    for tokens, heads, rels in sentences:
        p_heads, p_rels = predict_sentence(tokens)
        gold_heads.extend(heads)
        pred_heads.extend(p_heads)
        gold_rels.extend(rels)
        pred_rels.extend(p_rels)
        is_punct.extend([r == "punct" for r in rels])
    return (
        np.array(gold_heads),
        np.array(pred_heads),
        np.array(gold_rels),
        np.array(pred_rels),
        np.array(is_punct),
    )


def attachment_scores(gold_heads, pred_heads, gold_rels, pred_rels, mask=None):
    """UAS·LAS를 계산합니다. mask가 있으면 그 위치만 셉니다."""
    if mask is None:
        mask = np.ones(len(gold_heads), dtype=bool)
    head_ok = (gold_heads == pred_heads) & mask
    both_ok = head_ok & (gold_rels == pred_rels)
    n = mask.sum()
    uas = head_ok.sum() / n if n else 0.0
    las = both_ok.sum() / n if n else 0.0
    return uas, las


g_h, p_h, g_r, p_r, punct = collect_eval(test_sents)
uas, las = attachment_scores(g_h, p_h, g_r, p_r)
uas_c, las_c = attachment_scores(g_h, p_h, g_r, p_r, mask=~punct)
print("시험 UAS (지배소):", round(float(uas), 3), "/ LAS (지배소+관계):", round(float(las), 3))
print("문장부호 제외 UAS:", round(float(uas_c), 3), "/ LAS:", round(float(las_c), 3))
print("관계 이름만 맞힌 비율:", round(accuracy_score(g_r, p_r), 3))
print()


def format_rel(rel):
    """관계 이름을 'nsubj/주어'처럼 독일어 약호와 한글을 함께 보여 줍니다."""
    return f"{rel}/{REL_KO.get(rel, rel)}"


def print_conll(tokens, heads, rels, gold_heads=None, gold_rels=None):
    """한 문장을 표로 보여 줍니다. 정답이 있으면 맞음(O)/틀림(X)도 적습니다."""
    print(f"{'번호':<4} {'단어':<14} {'지배소':<8} {'관계':<16}", end="")
    if gold_heads is not None:
        print(f" {'정답지배소':<8} {'정답관계':<16} 판정")
    else:
        print()
    print("-" * (70 if gold_heads is None else 90))
    for i, token in enumerate(tokens):
        head_word = "ROOT" if heads[i] == 0 else tokens[heads[i] - 1]
        head_cell = f"{heads[i]}:{head_word}"
        line = f"{i + 1:<4} {token:<14} {head_cell:<8} {format_rel(rels[i]):<16}"
        if gold_heads is not None:
            g_word = "ROOT" if gold_heads[i] == 0 else tokens[gold_heads[i] - 1]
            g_cell = f"{gold_heads[i]}:{g_word}"
            ok = "O" if (heads[i] == gold_heads[i] and rels[i] == gold_rels[i]) else "X"
            line += f" {g_cell:<8} {format_rel(gold_rels[i]):<16} {ok}"
        print(line)


def print_tree(tokens, heads, rels):
    """의존 구조를 나무 모양으로 들여 써 보여 줍니다."""
    children = [[] for _ in tokens]
    roots = []
    for i, h in enumerate(heads):
        if h == 0:
            roots.append(i)
        else:
            children[h - 1].append(i)

    def walk(idx, prefix, is_last, is_root):
        label = f"{format_rel(rels[idx])}: {tokens[idx]}"
        if is_root:
            print(label)
        else:
            branch = "└─ " if is_last else "├─ "
            print(prefix + branch + label)
        kids = children[idx]
        if is_root:
            next_prefix = ""
        else:
            next_prefix = prefix + ("    " if is_last else "│   ")
        for k, child in enumerate(kids):
            walk(child, next_prefix, k == len(kids) - 1, False)

    if not roots:
        print("(뿌리를 찾지 못했습니다)")
        return
    for r in roots:
        walk(r, "", True, True)


print("시험 문장 분석 (O=맞음, X=틀림)")
for tokens, heads, rels in test_sents:
    pred_heads, pred_rels = predict_sentence(tokens)
    print()
    print("문장:", " ".join(tokens))
    print_conll(tokens, pred_heads, pred_rels, gold_heads=heads, gold_rels=rels)
    print("나무:")
    print_tree(tokens, pred_heads, pred_rels)
print()


# ---------------------------------------------------------------------------
# 6) 한 문장을 단계별로 풀어 보기
#    초보자가 "단어 → 창 → 오프셋 → 지배소 → 관계" 순서를 따라갈 수 있게
#    중간 결과를 출력합니다.
# ---------------------------------------------------------------------------
demo_tokens = ["Der", "Hund", "jagt", "die", "Katze", "."]
demo_heads, demo_rels = predict_sentence(demo_tokens)
print("단계별 예시:", " ".join(demo_tokens))
print(f"{'위치':<4} {'단어':<8} {'창(주변 단어)':<45} {'오프셋':<8} {'지배소':<10} {'관계'}")
print("-" * 95)
parser.eval()
demo_windows = np.array(
    [window_to_ids(word_window(demo_tokens, i), word_to_id) for i in range(len(demo_tokens))],
    dtype=np.int64,
)
with torch.no_grad():
    demo_off_ids = parser.score_heads(torch.tensor(demo_windows)).argmax(dim=1).numpy()
for i, tok in enumerate(demo_tokens):
    window_txt = " ".join(word_window(demo_tokens, i))
    offset = id_to_offset[int(demo_off_ids[i])]
    head = demo_heads[i]
    head_word = "ROOT" if head == 0 else demo_tokens[head - 1]
    print(f"{i:<4} {tok:<8} {window_txt:<45} {offset:<8} {head_word:<10} {format_rel(demo_rels[i])}")
print()
print("나무:")
print_tree(demo_tokens, demo_heads, demo_rels)
print()


# ---------------------------------------------------------------------------
# 7) 새 문장 분석
#    학습에 넣은 문장과, 비슷한 뼈대를 가진 새 문장을 함께 넣어 봅니다.
#    아래 리스트를 바꿔 가며 실행해 보세요.
# ---------------------------------------------------------------------------
print("참고용 분석 (정답 없이 모델 예측만)")
for text in [
    "Der Hund schläft .",
    "Die Lehrerin erklärt die Übung .",
    "Kleine Kinder spielen im Garten .",
    "Der junge Student hat ein Buch gelesen .",
]:
    tokens = text.split()
    heads, rels = predict_sentence(tokens)
    print()
    print("문장:", text)
    print_conll(tokens, heads, rels)
    print("나무:")
    print_tree(tokens, heads, rels)
print()


# ---------------------------------------------------------------------------
# 8) 의존 화살표 시각화
#    단어를 가로로 놓고, 의존소에서 지배소로 올라가는 호를 그립니다.
# ---------------------------------------------------------------------------
REL_COLORS = {
    "root": "#264653",
    "nsubj": "#2a9d8f",
    "obj": "#e76f51",
    "det": "#8ab17d",
    "amod": "#e9c46a",
    "advmod": "#f4a261",
    "case": "#6d597a",
    "obl": "#b56576",
    "aux": "#4c6ef5",
    "cop": "#748ffc",
    "punct": "#bbbbbb",
}


def draw_sentence(ax, tokens, heads, rels, title):
    """한 문장의 의존 호를 한 칸의 그래프에 그립니다."""
    n = len(tokens)
    ax.set_xlim(-0.6, n - 0.4)
    # 멀리 연결된 호일수록 더 높이 올라가게 해, 선이 겹치는 것을 줄입니다.
    max_span = max((abs((h - 1) - i) if h else 1) for i, h in enumerate(heads))
    ax.set_ylim(-0.55, 0.55 + 0.45 * max_span)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11)

    for i, tok in enumerate(tokens):
        ax.scatter([i], [0.02], s=18, color="black", zorder=3)
        ax.text(i, -0.12, tok, ha="center", va="top", fontsize=10)

    for i, (h, r) in enumerate(zip(heads, rels)):
        color = REL_COLORS.get(r, "#333333")
        if h == 0:
            ax.annotate(
                "ROOT",
                xy=(i, 0.06),
                xytext=(i, 0.55 + 0.15 * max_span),
                ha="center",
                va="bottom",
                fontsize=8,
                color=color,
                arrowprops=dict(arrowstyle="-", color=color, lw=1.2, ls="--"),
            )
            continue
        j = h - 1
        span = abs(j - i)
        height = 0.18 + 0.28 * span
        rad = 0.2 + 0.12 * span
        # rad를 음수로 두면 호가 단어 위쪽으로 올라갑니다.
        arrow = FancyArrowPatch(
            (i, 0.06),
            (j, 0.06),
            connectionstyle=f"arc3,rad={-rad}",
            arrowstyle="-|>",
            mutation_scale=9,
            lw=1.2,
            color=color,
        )
        ax.add_patch(arrow)
        mid = (i + j) / 2
        ax.text(mid, height, r, ha="center", va="bottom", fontsize=8, color=color)


show_sents = [
    "Der Hund schläft .",
    "Die Katze jagt die Maus .",
    "Der alte Mann trinkt Kaffee .",
    "Die Frau hat ein Buch gelesen .",
]

fig, axes = plt.subplots(len(show_sents), 1, figsize=(11, 2.4 * len(show_sents)))
if len(show_sents) == 1:
    axes = [axes]
for ax, text in zip(axes, show_sents):
    tokens = text.split()
    heads, rels = predict_sentence(tokens)
    draw_sentence(ax, tokens, heads, rels, text)

handles = [
    Patch(facecolor=REL_COLORS[name], edgecolor="none", label=f"{name} ({REL_KO[name]})")
    for name in ("root", "nsubj", "obj", "det", "amod", "advmod", "aux", "cop")
]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False)
plt.tight_layout(rect=(0, 0.06, 1, 1))
plt.show()
