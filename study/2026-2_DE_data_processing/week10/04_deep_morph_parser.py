"""딥러닝으로 독일어 단어를 형태소로 나누는 실습

형태소 분석이란:
- 단어를 더 작은 의미 단위(접두사, 어간, 접미사)로 쪼개는 일입니다.
- 예: unglaublich → un(접두사) + glaub(어간) + lich(접미사)

이 실습의 아이디어:
- 사람처럼 규칙을 직접 쓰지 않습니다.
- 글자마다 "이 글자는 접두사/어간/접미사의 어디인가?"라는 태그를 붙입니다.
- 각 글자를 작은 벡터(임베딩)로 바꾼 뒤, 03강과 같은 다층 신경망이
  주변 글자를 보고 태그를 예측합니다.
- 이어진 태그를 다시 모아 형태소를 복원합니다.

품사(형용사/명사/동사)는 단어 전체의 글자 n-그램 벡터로 따로 학습합니다.
02강의 단어 빈도 벡터와 같은 방법이고, 단위만 '단어'에서 '글자'로 바뀐 것입니다.
"""

# numpy: 숫자 벡터·행렬 계산
# torch: 딥러닝 계산 (글자 임베딩 + 신경망)
# matplotlib: 형태소 구간을 색으로 보여 주기
# MLPClassifier: 품사 분류용 다층 신경망 (03강과 같음)
# CountVectorizer: 글자 n-그램을 세어 벡터로 만듦 (02강과 같음)
# accuracy_score: 정답과 예측이 얼마나 맞는지 비율로 계산
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline

# Windows에서 그래프 한글이 깨지지 않도록 글꼴을 지정합니다.
plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)

# 실행할 때마다 같은 결과가 나오도록 난수를 고정합니다.
np.random.seed(42)
torch.manual_seed(42)


# ---------------------------------------------------------------------------
# 1) 작은 정답 데이터
#    실제 형태소 분석기는 수십만 단어를 쓰지만,
#    여기서는 "신경망이 글자 패턴을 배운다"는 장면만 보는 연습용 세트입니다.
#
#    각 항목: (단어, [(형태소, 종류), ...], 품사)
#    형태소를 순서대로 이어 붙이면 원래 단어가 되어야 합니다.
# ---------------------------------------------------------------------------
EXAMPLES = [
    # 형용사: 자주 보이는 접두사 un-, 접미사 -lich
    ("unglaublich", [("un", "PREF"), ("glaub", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("unfreundlich", [("un", "PREF"), ("freund", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("unglücklich", [("un", "PREF"), ("glück", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("unbekannt", [("un", "PREF"), ("bekannt", "STEM")], "ADJ"),
    ("unsichtbar", [("un", "PREF"), ("sicht", "STEM"), ("bar", "SUFF")], "ADJ"),
    ("unmöglich", [("un", "PREF"), ("mög", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("bekannt", [("bekannt", "STEM")], "ADJ"),
    ("freundlich", [("freund", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("möglich", [("mög", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("gefährlich", [("gefähr", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("glücklich", [("glück", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("täglich", [("täg", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("herzlich", [("herz", "STEM"), ("lich", "SUFF")], "ADJ"),
    ("schönste", [("schön", "STEM"), ("st", "SUFF"), ("e", "SUFF")], "ADJ"),
    # 명사: -ung, -heit, -schaft, -chen, -in, 복수 -er/-en
    ("Freundschaft", [("Freund", "STEM"), ("schaft", "SUFF")], "NOUN"),
    ("Wissenschaft", [("Wissen", "STEM"), ("schaft", "SUFF")], "NOUN"),
    ("Bedeutung", [("Bedeut", "STEM"), ("ung", "SUFF")], "NOUN"),
    ("Wohnung", [("Wohn", "STEM"), ("ung", "SUFF")], "NOUN"),
    ("Übung", [("Üb", "STEM"), ("ung", "SUFF")], "NOUN"),
    ("Zeitung", [("Zeit", "STEM"), ("ung", "SUFF")], "NOUN"),
    ("Freiheit", [("Frei", "STEM"), ("heit", "SUFF")], "NOUN"),
    ("Kindheit", [("Kind", "STEM"), ("heit", "SUFF")], "NOUN"),
    ("Wahrheit", [("Wahr", "STEM"), ("heit", "SUFF")], "NOUN"),
    ("Möglichkeit", [("Mög", "STEM"), ("lich", "SUFF"), ("keit", "SUFF")], "NOUN"),
    ("Mädchen", [("Mäd", "STEM"), ("chen", "SUFF")], "NOUN"),
    ("Häuschen", [("Häus", "STEM"), ("chen", "SUFF")], "NOUN"),
    ("Lehrerin", [("Lehr", "STEM"), ("er", "SUFF"), ("in", "SUFF")], "NOUN"),
    ("Studentin", [("Student", "STEM"), ("in", "SUFF")], "NOUN"),
    ("Lehrer", [("Lehr", "STEM"), ("er", "SUFF")], "NOUN"),
    ("Spieler", [("Spiel", "STEM"), ("er", "SUFF")], "NOUN"),
    ("Häuser", [("Häus", "STEM"), ("er", "SUFF")], "NOUN"),
    ("Bücher", [("Büch", "STEM"), ("er", "SUFF")], "NOUN"),
    ("Studenten", [("Student", "STEM"), ("en", "SUFF")], "NOUN"),
    ("Kinder", [("Kind", "STEM"), ("er", "SUFF")], "NOUN"),
    # 동사: 부정사 -en, 과거분사 ge- … -t/-en, 접두사 ver-/be-/er-/ent-/zer-
    ("spielen", [("spiel", "STEM"), ("en", "SUFF")], "VERB"),
    ("machen", [("mach", "STEM"), ("en", "SUFF")], "VERB"),
    ("sagen", [("sag", "STEM"), ("en", "SUFF")], "VERB"),
    ("gehen", [("geh", "STEM"), ("en", "SUFF")], "VERB"),
    ("kaufen", [("kauf", "STEM"), ("en", "SUFF")], "VERB"),
    ("verstehen", [("ver", "PREF"), ("steh", "STEM"), ("en", "SUFF")], "VERB"),
    ("vergessen", [("ver", "PREF"), ("gess", "STEM"), ("en", "SUFF")], "VERB"),
    ("verkaufen", [("ver", "PREF"), ("kauf", "STEM"), ("en", "SUFF")], "VERB"),
    ("besuchen", [("be", "PREF"), ("such", "STEM"), ("en", "SUFF")], "VERB"),
    ("bezahlen", [("be", "PREF"), ("zahl", "STEM"), ("en", "SUFF")], "VERB"),
    ("bekommen", [("be", "PREF"), ("komm", "STEM"), ("en", "SUFF")], "VERB"),
    ("erzählen", [("er", "PREF"), ("zähl", "STEM"), ("en", "SUFF")], "VERB"),
    ("erklären", [("er", "PREF"), ("klär", "STEM"), ("en", "SUFF")], "VERB"),
    ("erfinden", [("er", "PREF"), ("find", "STEM"), ("en", "SUFF")], "VERB"),
    ("entscheiden", [("ent", "PREF"), ("scheid", "STEM"), ("en", "SUFF")], "VERB"),
    ("entfernen", [("ent", "PREF"), ("fern", "STEM"), ("en", "SUFF")], "VERB"),
    ("zerstören", [("zer", "PREF"), ("stör", "STEM"), ("en", "SUFF")], "VERB"),
    ("zerlegen", [("zer", "PREF"), ("leg", "STEM"), ("en", "SUFF")], "VERB"),
    ("gemacht", [("ge", "PREF"), ("mach", "STEM"), ("t", "SUFF")], "VERB"),
    ("gesagt", [("ge", "PREF"), ("sag", "STEM"), ("t", "SUFF")], "VERB"),
    ("gespielt", [("ge", "PREF"), ("spiel", "STEM"), ("t", "SUFF")], "VERB"),
    ("gekauft", [("ge", "PREF"), ("kauf", "STEM"), ("t", "SUFF")], "VERB"),
    ("gesehen", [("ge", "PREF"), ("seh", "STEM"), ("en", "SUFF")], "VERB"),
    ("gegangen", [("ge", "PREF"), ("gang", "STEM"), ("en", "SUFF")], "VERB"),
]

# 화면에 한글로 보여 줄 이름
TAG_KO = {"PREF": "접두사", "STEM": "어간", "SUFF": "접미사"}
POS_KO = {"ADJ": "형용사", "NOUN": "명사", "VERB": "동사"}

# 글자 창의 반지름. 2이면 왼쪽 2글자 + 자기 자신 + 오른쪽 2글자 = 5글자를 봅니다.
WINDOW = 2
PAD = "<PAD>"  # 단어 맨 앞·뒤에 칸이 모자랄 때 채우는 빈 글자
UNK = "<UNK>"  # 학습 때 본 적 없는 글자


def check_examples(examples):
    """형태소를 이어 붙인 결과가 단어와 같은지 검사합니다. 데이터 입력 실수를 막습니다."""
    for word, morphs, _pos in examples:
        joined = "".join(piece for piece, _tag in morphs)
        if joined != word:
            raise ValueError(f"형태소 합이 단어와 다릅니다: {word} != {joined}")


# ---------------------------------------------------------------------------
# 2) 글자마다 태그 붙이기 (BIO 표기)
#
#    B(Begin): 그 형태소의 첫 글자
#    I(Inside): 그 형태소의 나머지 글자
#
#    BIO가 필요한 이유:
#    Lehrerin = Lehr + er + in 처럼 접미사가 두 번 이어질 수 있습니다.
#    글자 태그가 모두 SUFF이면 'erin'으로 붙어 버리므로,
#    B-SUFF / I-SUFF 로 "새 형태소가 시작된다"를 표시합니다.
# ---------------------------------------------------------------------------
def word_to_char_tags(word, morphs):
    """단어의 각 글자에 BIO 태그를 붙입니다.

    예: un + glaub + lich
        u:B-PREF n:I-PREF g:B-STEM l:I-STEM ... l:B-SUFF i:I-SUFF ...
    """
    tags = []
    for piece, label in morphs:
        for i, _ch in enumerate(piece):
            prefix = "B" if i == 0 else "I"
            tags.append(f"{prefix}-{label}")
    if len(tags) != len(word):
        raise ValueError(f"글자 수와 태그 수가 다릅니다: {word}")
    return tags


def char_window(word, index, window=WINDOW):
    """한 글자를 판단할 때 함께 볼 주변 글자 목록을 만듭니다.

    예: 'unglaublich'의 0번째 'u' → ['<PAD>', '<PAD>', 'u', 'n', 'g']
    앞뒤가 없으면 PAD로 채워, 모든 글자가 같은 길이의 입력을 갖게 합니다.
    """
    chars = []
    for offset in range(-window, window + 1):
        j = index + offset
        if 0 <= j < len(word):
            chars.append(word[j])
        else:
            chars.append(PAD)
    return chars


def build_char_vocab(words):
    """학습 단어에 나온 글자 + PAD/UNK 를 번호로 매깁니다.

    신경망은 글자 자체를 받지 못하고 숫자만 받습니다.
    그래서 'a'→3, 'ü'→28 처럼 변환표가 필요합니다.
    """
    charset = set()
    for word in words:
        charset.update(word)
    # 정렬하면 실행할 때마다 같은 번호가 나와 결과가 재현됩니다.
    symbols = [PAD, UNK] + sorted(charset)
    return {ch: i for i, ch in enumerate(symbols)}


def window_to_ids(window_chars, char_to_id):
    """글자 창을 번호 목록으로 바꿉니다. 모르는 글자는 UNK 번호를 씁니다."""
    unk = char_to_id[UNK]
    return [char_to_id.get(ch, unk) for ch in window_chars]


def make_tag_dataset(examples, char_to_id):
    """모든 단어의 모든 글자를 (창 번호, 정답 태그) 한 줄로 펼칩니다.

    단어 단위가 아니라 글자 단위로 학습합니다.
    한 단어가 11글자면 학습 샘플이 11개 생깁니다.
    """
    X, y = [], []
    for word, morphs, _pos in examples:
        tags = word_to_char_tags(word, morphs)
        for i, tag in enumerate(tags):
            X.append(window_to_ids(char_window(word, i), char_to_id))
            y.append(tag)
    return np.array(X, dtype=np.int64), y


def tags_to_morphs(word, tags):
    """글자 태그를 다시 형태소 조각으로 합칩니다.

    B-가 나오거나 종류(PREF/STEM/SUFF)가 바뀌면 새 형태소를 시작합니다.
    """
    morphs = []
    buf, current = [], None
    for ch, tag in zip(word, tags):
        _bio, label = tag.split("-", 1)
        start_new = (current is None) or tag.startswith("B-") or (label != current)
        if start_new and buf:
            morphs.append(("".join(buf), current))
            buf = []
        buf.append(ch)
        current = label
    if buf:
        morphs.append(("".join(buf), current))
    return morphs


def format_morphs(morphs):
    """형태소 목록을 'un/접두사 + glaub/어간 + lich/접미사' 문자열로 만듭니다."""
    parts = [f"{piece}/{TAG_KO.get(label, label)}" for piece, label in morphs]
    return " + ".join(parts)


# ---------------------------------------------------------------------------
# 3) 데이터 준비: 단어 단위로 학습/시험 분리
#
#    글자 단위로 나누면 같은 단어의 글자가 학습과 시험에 섞입니다.
#    그러면 "처음 보는 단어"를 시험하는 것이 아니므로, 단어를 먼저 나눕니다.
#
#    시험 단어는 통째로 학습에 넣지 않되, 접두사·접미사는 다른 단어에서
#    이미 본 조합으로 고릅니다. 신경망이 글자 패턴을 옮겨 쓰는지 보기 위해서입니다.
#    예: 학습에 unfreundlich, möglich → 시험의 unmöglich 을 un + mög + lich 로 나눌 수 있는지
# ---------------------------------------------------------------------------
check_examples(EXAMPLES)

TEST_WORDS = {
    "freundlich", "unmöglich", "Studentin", "Kinder", "Zeitung",
    "verkaufen", "gesagt", "gekauft", "besuchen", "zerlegen",
}

train_ex = [ex for ex in EXAMPLES if ex[0] not in TEST_WORDS]
test_ex = [ex for ex in EXAMPLES if ex[0] in TEST_WORDS]
if len(test_ex) != len(TEST_WORDS):
    missing = TEST_WORDS - {ex[0] for ex in test_ex}
    raise ValueError(f"시험 단어가 데이터에 없습니다: {missing}")

# 변환표는 학습 단어의 글자만으로 만듭니다.
# 시험 단어의 새 글자는 UNK로 처리하는 것이 "본 적 없는 입력"에 가깝습니다.
char_to_id = build_char_vocab([ex[0] for ex in train_ex])
X_train, y_train = make_tag_dataset(train_ex, char_to_id)
X_test, y_test = make_tag_dataset(test_ex, char_to_id)

# 태그 문자열도 번호로 바꿉니다. 신경망의 출력 칸 하나가 태그 하나에 해당합니다.
tag_names = sorted(set(y_train))
tag_to_id = {tag: i for i, tag in enumerate(tag_names)}
id_to_tag = {i: tag for tag, i in tag_to_id.items()}
y_train_id = np.array([tag_to_id[tag] for tag in y_train], dtype=np.int64)

print("학습 단어 수:", len(train_ex), "/ 시험 단어 수:", len(test_ex))
print("글자 종류 수(PAD/UNK 포함):", len(char_to_id))
print("태그 종류:", ", ".join(tag_names))
print("학습 글자 샘플 수:", len(y_train), "/ 시험 글자 샘플 수:", len(y_test))
print()


# ---------------------------------------------------------------------------
# 4) 형태소 태그 신경망 (글자 임베딩 + 다층 퍼셉트론)
#
#    02강 벡터: 사람이 횟수를 세어 만든 값
#    여기 임베딩: 학습이 스스로 찾는 작은 글자 벡터
#                 같은 역할의 글자(예: 접두사 자리의 u, g, e)가 비슷한 숫자를 갖게 됩니다.
#
#    구조: 창의 각 글자 → 임베딩 → 이어 붙임 → 은닉층 → 태그 점수
# ---------------------------------------------------------------------------
class MorphTagger(nn.Module):
    """주변 글자를 보고 한 글자의 BIO 태그를 예측하는 작은 신경망입니다."""

    def __init__(self, vocab_size, n_tags, emb_dim=16, hidden=64, window_size=2 * WINDOW + 1):
        super().__init__()
        # 글자 번호 → 길이 16짜리 벡터. 이 숫자들은 학습하면서 바뀝니다.
        self.emb = nn.Embedding(vocab_size, emb_dim)
        # 창이 5글자면 5 * 16 = 80차원 입력이 은닉층으로 들어갑니다.
        self.hidden = nn.Linear(emb_dim * window_size, hidden)
        self.out = nn.Linear(hidden, n_tags)

    def forward(self, char_ids):
        # char_ids 모양: (샘플 수, 창 길이)
        # 임베딩 후 모양: (샘플 수, 창 길이, 16) → 한 줄로 펼침
        vectors = self.emb(char_ids)
        flat = vectors.reshape(char_ids.size(0), -1)
        # relu: 음수는 0으로 만들어, 03강의 다층 신경망처럼 굽은 경계를 그릴 수 있게 합니다.
        hidden = torch.relu(self.hidden(flat))
        return self.out(hidden)


tagger = MorphTagger(vocab_size=len(char_to_id), n_tags=len(tag_names))

# 텐서: 파이토치가 기울기(얼마나 고칠지)를 계산할 수 있는 숫자 묶음
X_train_t = torch.tensor(X_train)
y_train_t = torch.tensor(y_train_id)
X_test_t = torch.tensor(X_test)

# CrossEntropyLoss: 정답 태그의 점수는 높이고, 다른 태그의 점수는 낮추도록 차이를 재는 함수
# Adam: 그 차이를 줄이는 방향으로 가중치를 조금씩 수정하는 최적화 방법
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(tagger.parameters(), lr=0.01)

n_epochs = 120  # 학습 데이터를 120번 반복해 봅니다.
for epoch in range(1, n_epochs + 1):
    tagger.train()
    scores = tagger(X_train_t)          # 각 태그에 대한 점수
    loss = loss_fn(scores, y_train_t)   # 정답과 얼마나 다른지
    optimizer.zero_grad()               # 직전 반복의 수정량을 지움
    loss.backward()                     # 각 가중치를 어느 쪽으로 고칠지 계산
    optimizer.step()                    # 실제로 조금 수정
    if epoch in (1, 40, 80, 120):
        print(f"학습 {epoch:3d}번째, 손실(작을수록 좋음): {loss.item():.3f}")


def predict_tag_ids(char_id_matrix):
    """글자 창 번호 배열을 받아 태그 번호 배열을 돌려줍니다."""
    tagger.eval()
    with torch.no_grad():  # 예측만 할 때는 수정량 계산이 필요 없습니다.
        scores = tagger(torch.tensor(char_id_matrix))
        return scores.argmax(dim=1).numpy()  # 점수가 가장 큰 태그를 선택


tag_pred = [id_to_tag[i] for i in predict_tag_ids(X_test)]
print("글자 태그 정확도:", round(accuracy_score(y_test, tag_pred), 3))


# ---------------------------------------------------------------------------
# 5) 품사 신경망
#    단어 하나를 글자 2~3그램 빈도 벡터로 바꾼 뒤 MLP로 형용사/명사/동사를 예측합니다.
#    예: "gespielt" 안에는 ge, sp, ie, el, lt, spi, pie ... 조각이 들어 있습니다.
# ---------------------------------------------------------------------------
train_words = [ex[0] for ex in train_ex]
train_pos = [ex[2] for ex in train_ex]
test_words = [ex[0] for ex in test_ex]
test_pos = [ex[2] for ex in test_ex]

pos_model = make_pipeline(
    CountVectorizer(analyzer="char", ngram_range=(2, 3)),
    MLPClassifier(hidden_layer_sizes=(32,), max_iter=800, random_state=42),
)
pos_model.fit(train_words, train_pos)
pos_pred = pos_model.predict(test_words)
print("품사 정확도:", round(accuracy_score(test_pos, pos_pred), 3))
print()


def predict_tags(word):
    """한 단어의 각 글자에 대해 형태소 태그를 예측합니다."""
    windows = np.array(
        [window_to_ids(char_window(word, i), char_to_id) for i in range(len(word))],
        dtype=np.int64,
    )
    return [id_to_tag[i] for i in predict_tag_ids(windows)]


def analyze(word, gold_morphs=None, gold_pos=None):
    """단어를 형태소로 나누고 품사를 예측해 한 줄로 보여 줍니다."""
    tags = predict_tags(word)
    morphs = tags_to_morphs(word, tags)
    pos = pos_model.predict([word])[0]
    line = f"{word:15} {format_morphs(morphs):40} 품사: {POS_KO[pos]}"
    if gold_morphs is not None:
        gold_txt = format_morphs(gold_morphs)
        ok = "O" if morphs == gold_morphs else "X"
        line += f"  | 정답: {gold_txt} [{ok}]"
    if gold_pos is not None:
        pos_ok = "O" if pos == gold_pos else "X"
        line += f" / {POS_KO[gold_pos]} [{pos_ok}]"
    print(line)
    return morphs, pos


print("시험 단어 분석 (O=맞음, X=틀림)")
for word, morphs, pos in test_ex:
    analyze(word, gold_morphs=morphs, gold_pos=pos)
print()
print("작은 데이터에서는 비슷한 글자 패턴을 섞어 보기도 합니다.")
print("예: ge- 는 gemacht의 접두사이기도 하고, gefährlich의 앞부분이기기도 합니다.")
print()


# ---------------------------------------------------------------------------
# 6) 한 단어를 단계별로 풀어 보기
#    초보자가 "글자 → 창 → 태그 → 형태소" 순서를 따라갈 수 있게 중간 결과를 출력합니다.
# ---------------------------------------------------------------------------
demo_word = "unglaublich"
demo_tags = predict_tags(demo_word)
print(f"단계별 예시: {demo_word}")
print("위치 | 글자 | 창(주변 글자)           | 예측 태그")
print("-" * 58)
for i, ch in enumerate(demo_word):
    window_chars = char_window(demo_word, i)
    window_txt = " ".join(window_chars)
    print(f"{i:4} | {ch:^4} | {window_txt:22} | {demo_tags[i]}")
print("→", format_morphs(tags_to_morphs(demo_word, demo_tags)))
print()


# ---------------------------------------------------------------------------
# 7) 새 단어 분석
#    학습에 넣은 단어와, 비슷한 접사가 있는 새 단어를 함께 넣어 봅니다.
#    아래 리스트를 바꿔 가며 실행해 보세요.
# ---------------------------------------------------------------------------
print("참고용 분석 (정답 없이 모델 예측만)")
for word in ["Freundschaft", "gespielt", "unmöglich", "erklären", "Kindheit"]:
    analyze(word)
print()


# ---------------------------------------------------------------------------
# 8) 형태소 구간 시각화
#    한 막대 안에서 접두사/어간/접미사를 다른 색으로 칠합니다.
# ---------------------------------------------------------------------------
COLORS = {"PREF": "#f4a261", "STEM": "#2a9d8f", "SUFF": "#e9c46a"}
show_words = ["unglaublich", "Freundschaft", "gespielt", "Lehrerin", "verstehen", "Häuschen"]

fig, ax = plt.subplots(figsize=(10, 4.5))
for row, word in enumerate(show_words):
    morphs = tags_to_morphs(word, predict_tags(word))
    x = 0
    for piece, label in morphs:
        width = max(len(piece), 1)
        ax.barh(row, width, left=x, color=COLORS.get(label, "#cccccc"), edgecolor="black", height=0.6)
        ax.text(x + width / 2, row, piece, ha="center", va="center", fontsize=10)

ax.set_yticks(range(len(show_words)))
ax.set_yticklabels(show_words)
ax.invert_yaxis()  # 리스트의 첫 단어를 그래프 위쪽에 둡니다.
ax.set_xlabel("글자 위치")
ax.set_title("딥러닝 형태소 분석: 접두사(주황) / 어간(초록) / 접미사(노랑)")
ax.legend(
    handles=[Patch(facecolor=COLORS[k], edgecolor="black", label=TAG_KO[k]) for k in ("PREF", "STEM", "SUFF")],
    loc="lower right",
)

plt.tight_layout()
plt.show()
