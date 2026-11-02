"""딥러닝으로 독일어 문장의 의미를 분석하는 실습

의미 분석이란:
- 05강의 의존 문법은 "주어·목적어가 누구인가"처럼 문장 뼈대를 봅니다.
- 의미 분석은 한 걸음 더 가서 "누가 하고, 무엇이 당하는가"를 묻습니다.
- 주어가 항상 행위자는 아닙니다.
    Der Hund schläft.          주어 Hund = 행위자 (자신이 잔다)
    Der Brief wird geschrieben. 주어 Brief = 대상 (편지가 쓰여진다)
    Die Blume ist schön.        주어 Blume = 테마 (꽃이 어떤 상태인가)

의미역(semantic role)이란:
- 서술어(동사)를 중심에 두고, 각 구가 그 사건에서 맡은 역할입니다.
- 예: Der Hund jagt die Katze.
      서술어 jagt, 행위자 Der Hund, 대상 die Katze
      논리식: jagt(AGT=Der Hund, PAT=die Katze)

이 실습의 아이디어:
- 독일어 격·어순 규칙을 직접 쓰지 않습니다.
- 각 단어마다 의미역 태그 하나를 예측합니다.
- 같은 태그가 이어지면 한 구(덩어리)로 합칩니다.
- 04강·05강과 같이 단어를 작은 벡터(임베딩)로 바꾼 뒤,
  주변 단어를 보는 다층 신경망이 태그를 찾습니다.

실제 분석기는 훨씬 큰 말뭉치와 양방향 LSTM·트랜스포머를 씁니다.
여기서는 "신경망이 단어 패턴으로 의미 구조를 배운다"는 장면만 봅니다.
"""

# numpy: 숫자 벡터·행렬 계산
# torch: 딥러닝 계산 (단어 임베딩 + 신경망)
# matplotlib: 의미역 구간을 색 상자로 보여 주기
# accuracy_score: 정답과 예측이 얼마나 맞는지 비율로 계산
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from sklearn.metrics import accuracy_score

# Windows에서 그래프 한글이 깨지지 않도록 글꼴을 지정합니다.
plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)

# 실행할 때마다 같은 결과가 나오도록 난수를 고정합니다.
np.random.seed(42)
torch.manual_seed(42)


# ---------------------------------------------------------------------------
# 1) 작은 정답 데이터
#    실제 의미역 분석기는 FrameNet·PropBank 같은 말뭉치(수만 문장)를 쓰지만,
#    여기서는 짧은 독일어 문장으로 "누가·무엇을·어디서"를 배운다는 연습만 합니다.
#
#    각 항목: (단어 목록, 의미역 태그 목록)
#    태그는 단어마다 하나씩입니다. 같은 태그가 이어지면 나중에 한 구로 합칩니다.
#
#    태그 이름:
#      PRED 서술어   사건의 중심 (본동사, 과거분사, 계사)
#      AGT  행위자   일을 하는 쪽 (흔히 주격, 그러나 항상은 아님)
#      PAT  대상     일을 당하는 쪽 (흔히 대격)
#      REC  수혜자   받는 쪽 (흔히 여격)
#      THM  테마     상태가 말해지는 쪽 (계사 문장의 주어)
#      ATTR 속성     어떤 상태인가 (schön, kalt)
#      LOC  장소     어디서
#      TMP  시간     언제
#      MNR  방식     어떻게
#      NEG  부정     nicht
#      O    없음     조동사 hat/wird, 문장부호
# ---------------------------------------------------------------------------
SENTENCES = [
    # 자동사: 행위자가 스스로 하는 일
    (["Der", "Hund", "schläft", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Die", "Katze", "schläft", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Das", "Kind", "schläft", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Der", "Student", "liest", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Die", "Lehrerin", "spricht", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Das", "Kind", "lacht", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Die", "Kinder", "spielen", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Der", "Mann", "trinkt", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Die", "Frau", "kauft", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Die", "Maus", "läuft", "."],
     ["AGT", "AGT", "PRED", "O"]),
    # 타동사: 행위자 + 서술어 + 대상
    (["Der", "Hund", "jagt", "die", "Katze", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Die", "Katze", "jagt", "die", "Maus", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Der", "Student", "liest", "ein", "Buch", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Die", "Lehrerin", "erklärt", "die", "Übung", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Die", "Frau", "kauft", "Brot", "."],
     ["AGT", "AGT", "PRED", "PAT", "O"]),
    (["Der", "Mann", "trinkt", "Kaffee", "."],
     ["AGT", "AGT", "PRED", "PAT", "O"]),
    (["Ein", "Kind", "schreibt", "einen", "Brief", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Die", "Lehrerin", "lobt", "den", "Studenten", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Der", "Hund", "jagt", "den", "Mann", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Die", "Kinder", "lesen", "ein", "Buch", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Das", "Kind", "mag", "die", "Katze", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Die", "Lehrerin", "mag", "die", "Kinder", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    # 형용사가 명사 구 안에 들어가면 그 구의 의미역을 함께 갖습니다.
    (["Kleine", "Kinder", "spielen", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Der", "alte", "Mann", "trinkt", "Kaffee", "."],
     ["AGT", "AGT", "AGT", "PRED", "PAT", "O"]),
    (["Die", "junge", "Frau", "kauft", "Brot", "."],
     ["AGT", "AGT", "AGT", "PRED", "PAT", "O"]),
    (["Das", "kleine", "Kind", "lacht", "."],
     ["AGT", "AGT", "AGT", "PRED", "O"]),
    (["Der", "junge", "Student", "liest", "."],
     ["AGT", "AGT", "AGT", "PRED", "O"]),
    (["Die", "alte", "Katze", "schläft", "."],
     ["AGT", "AGT", "AGT", "PRED", "O"]),
    # 방식(MNR), 시간(TMP), 부정(NEG)
    (["Der", "Hund", "schläft", "gern", "."],
     ["AGT", "AGT", "PRED", "MNR", "O"]),
    (["Die", "Kinder", "spielen", "heute", "."],
     ["AGT", "AGT", "PRED", "TMP", "O"]),
    (["Der", "Student", "liest", "langsam", "."],
     ["AGT", "AGT", "PRED", "MNR", "O"]),
    (["Die", "Katze", "schläft", "nicht", "."],
     ["AGT", "AGT", "PRED", "NEG", "O"]),
    (["Die", "Frau", "kauft", "heute", "Brot", "."],
     ["AGT", "AGT", "PRED", "TMP", "PAT", "O"]),
    (["Der", "Mann", "trinkt", "gern", "Kaffee", "."],
     ["AGT", "AGT", "PRED", "MNR", "PAT", "O"]),
    (["Die", "Lehrerin", "erklärt", "die", "Übung", "nicht", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "NEG", "O"]),
    (["Das", "Kind", "schreibt", "morgen", "."],
     ["AGT", "AGT", "PRED", "TMP", "O"]),
    (["Die", "Kinder", "spielen", "schnell", "."],
     ["AGT", "AGT", "PRED", "MNR", "O"]),
    # 장소: 전치사와 명사를 한 장소 구로 묶습니다.
    (["Die", "Kinder", "spielen", "im", "Garten", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "O"]),
    (["Der", "Hund", "schläft", "im", "Haus", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "O"]),
    (["Die", "Katze", "sitzt", "auf", "dem", "Tisch", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "LOC", "O"]),
    (["Der", "Student", "liest", "in", "der", "Bibliothek", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "LOC", "O"]),
    (["Das", "Kind", "spielt", "im", "Garten", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "O"]),
    (["Die", "Frau", "kauft", "Brot", "im", "Haus", "."],
     ["AGT", "AGT", "PRED", "PAT", "LOC", "LOC", "O"]),
    (["Der", "Mann", "sitzt", "in", "der", "Bibliothek", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "LOC", "O"]),
    # 완료 시제: 조동사 hat 은 의미가 아니라 시제 표시 → O
    #            과거분사(본동사)가 서술어
    (["Der", "Student", "hat", "ein", "Buch", "gelesen", "."],
     ["AGT", "AGT", "O", "PAT", "PAT", "PRED", "O"]),
    (["Die", "Lehrerin", "hat", "die", "Übung", "erklärt", "."],
     ["AGT", "AGT", "O", "PAT", "PAT", "PRED", "O"]),
    (["Das", "Kind", "hat", "Brot", "gekauft", "."],
     ["AGT", "AGT", "O", "PAT", "PRED", "O"]),
    (["Der", "Mann", "hat", "Kaffee", "getrunken", "."],
     ["AGT", "AGT", "O", "PAT", "PRED", "O"]),
    (["Die", "Kinder", "haben", "im", "Garten", "gespielt", "."],
     ["AGT", "AGT", "O", "LOC", "LOC", "PRED", "O"]),
    (["Die", "Katze", "hat", "die", "Maus", "gejagt", "."],
     ["AGT", "AGT", "O", "PAT", "PAT", "PRED", "O"]),
    # 계사 ist: 주어는 테마, 형용사는 속성
    # 05강에서는 형용사 schön 이 뿌리였지만,
    # 의미 분석에서는 "이다" 관계가 서술어이고 형용사는 값입니다.
    (["Die", "Blume", "ist", "schön", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Das", "Wetter", "ist", "kalt", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Der", "Hund", "ist", "alt", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Die", "Übung", "ist", "leicht", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Das", "Buch", "ist", "schön", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Die", "Katze", "ist", "klein", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Der", "Garten", "ist", "schön", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Die", "Lehrerin", "ist", "jung", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    # 수여 동사: 여격 = 수혜자, 대격 = 대상
    # der 는 주격 남성(Der Hund)일 수도, 여격 여성(der Frau)일 수도 있습니다.
    # 창 안의 동사·명사가 어느 쪽인지 가려 줍니다.
    (["Die", "Lehrerin", "gibt", "dem", "Kind", "das", "Buch", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "PAT", "O"]),
    (["Der", "Mann", "gibt", "der", "Frau", "Brot", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "O"]),
    (["Die", "Frau", "gibt", "dem", "Kind", "Kaffee", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "O"]),
    (["Das", "Kind", "gibt", "der", "Katze", "Brot", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "O"]),
    (["Der", "Student", "gibt", "der", "Lehrerin", "ein", "Buch", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "PAT", "O"]),
    (["Die", "Lehrerin", "zeigt", "dem", "Kind", "die", "Übung", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "PAT", "O"]),
    (["Der", "Mann", "bringt", "der", "Frau", "Kaffee", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "O"]),
    # 수동태: 주격 명사가 행위자가 아니라 대상입니다.
    # 05강의 nsubj 와 06강의 PAT 가 갈라지는 지점입니다.
    # 조동사 wird 는 O, 과거분사가 PRED.
    (["Der", "Brief", "wird", "geschrieben", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
    (["Die", "Übung", "wird", "erklärt", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
    (["Das", "Buch", "wird", "gelesen", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
    (["Der", "Student", "wird", "gelobt", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
    (["Die", "Maus", "wird", "gejagt", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
    (["Brot", "wird", "gekauft", "."],
     ["PAT", "O", "PRED", "O"]),
    (["Kaffee", "wird", "getrunken", "."],
     ["PAT", "O", "PRED", "O"]),
    (["Die", "Katze", "wird", "gelobt", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
]

# 화면에 한글로 보여 줄 의미역 이름
ROLE_KO = {
    "PRED": "서술어",
    "AGT": "행위자",
    "PAT": "대상",
    "REC": "수혜자",
    "THM": "테마",
    "ATTR": "속성",
    "LOC": "장소",
    "TMP": "시간",
    "MNR": "방식",
    "NEG": "부정",
    "O": "없음",
}

# 논리식을 질문으로 풀어 줄 때 쓰는 말
ROLE_QA = {
    "PRED": "무슨 일?",
    "AGT": "누가?",
    "PAT": "무엇을/누구를?",
    "REC": "누구에게?",
    "THM": "무엇이?",
    "ATTR": "어떤 상태?",
    "LOC": "어디서?",
    "TMP": "언제?",
    "MNR": "어떻게?",
    "NEG": "부정?",
}

# 단어 창의 반지름. 3이면 왼쪽 3단어 + 자기 자신 + 오른쪽 3단어 = 7단어를 봅니다.
# 짧은 문장에서는 문장 거의 전체가 창 안에 들어옵니다.
WINDOW = 3
PAD = "<PAD>"  # 문장 맨 앞·뒤에 칸이 모자랄 때 채우는 빈 칸
UNK = "<UNK>"  # 학습 때 본 적 없는 단어


def check_sentences(sentences):
    """단어 수와 태그 수가 같은지, 모르는 태그가 없는지 검사합니다."""
    known = set(ROLE_KO)
    for tokens, tags in sentences:
        if len(tokens) != len(tags):
            raise ValueError(f"길이가 다릅니다: {tokens}")
        unknown = set(tags) - known
        if unknown:
            raise ValueError(f"모르는 태그 {unknown}: {tokens}")
        if "PRED" not in tags:
            raise ValueError(f"서술어(PRED)가 없습니다: {tokens}")


# ---------------------------------------------------------------------------
# 2) 각 단어를 주변 단어 창으로 표현하기
#
#    04강: 글자 하나 + 양쪽 글자 → 형태소 태그
#    05강: 단어 하나 + 양쪽 단어 → 지배소 위치 + 관계 이름
#    06강: 단어 하나 + 양쪽 단어 → 의미역
#
#    창이 필요한 이유:
#    'Der'만 보면 행위자의 관사인지, 여격 수혜자(der Frau)인지 알 수 없습니다.
#    오른쪽이 Hund schläft 이면 행위자, gibt der Frau 이면 수혜자 쪽일 가능성이 큽니다.
#    'Brief'만 보면 목적어인지 수동태 주어인지 모릅니다.
#    오른쪽에 wird geschrieben 이 있으면 대상(PAT)입니다.
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
    """학습 문장에 나온 단어 + PAD/UNK 를 번호로 매깁니다.

    신경망은 글자열을 받지 못하고 숫자만 받습니다.
    그래서 Hund→7, schläft→18 처럼 변환표가 필요합니다.
    """
    vocab = set()
    for tokens in token_lists:
        vocab.update(tokens)
    symbols = [PAD, UNK] + sorted(vocab)
    return {w: i for i, w in enumerate(symbols)}


def window_to_ids(window_words, word_to_id):
    """단어 창을 번호 목록으로 바꿉니다. 모르는 단어는 UNK 번호를 씁니다."""
    unk = word_to_id[UNK]
    return [word_to_id.get(w, unk) for w in window_words]


def make_dataset(sentences, word_to_id, role_to_id):
    """모든 문장의 모든 단어를 학습 한 줄로 펼칩니다.

    한 문장이 4단어이면 샘플이 4개 생깁니다.
    각 줄에는 주변 단어 창 번호와 정답 의미역 번호가 들어갑니다.
    """
    windows, y_role = [], []
    for tokens, tags in sentences:
        for i, _token in enumerate(tokens):
            windows.append(window_to_ids(word_window(tokens, i), word_to_id))
            y_role.append(role_to_id[tags[i]])
    return np.array(windows, dtype=np.int64), np.array(y_role, dtype=np.int64)


def tags_to_spans(tokens, tags):
    """단어별 태그를 (역할, 구 텍스트) 목록으로 합칩니다.

    예: Der/AGT Hund/AGT jagt/PRED die/PAT Katze/PAT ./O
        → [('AGT', 'Der Hund'), ('PRED', 'jagt'), ('PAT', 'die Katze')]
    O(없음)는 구에 넣지 않습니다.
    """
    spans = []
    buf, current = [], None
    for token, tag in zip(tokens, tags):
        if tag == "O":
            if buf:
                spans.append((current, " ".join(buf)))
                buf, current = [], None
            continue
        if tag != current and buf:
            spans.append((current, " ".join(buf)))
            buf = []
        buf.append(token)
        current = tag
    if buf:
        spans.append((current, " ".join(buf)))
    return spans


def format_role(role):
    """의미역을 'AGT/행위자'처럼 약호와 한글을 함께 보여 줍니다."""
    return f"{role}/{ROLE_KO.get(role, role)}"


def format_logic(spans):
    """의미역 구를 논리식 문자열로 만듭니다.

    예: jagt(AGT=Der Hund, PAT=die Katze)
    """
    preds = [text for role, text in spans if role == "PRED"]
    args = [(role, text) for role, text in spans if role != "PRED"]
    pred_txt = preds[0] if preds else "?"
    arg_txt = ", ".join(f"{role}={text}" for role, text in args)
    return f"{pred_txt}({arg_txt})"


# ---------------------------------------------------------------------------
# 3) 데이터 준비: 문장 단위로 학습/시험 분리
#
#    단어 단위로 나누면 같은 문장의 단어가 학습과 시험에 섞입니다.
#    그러면 "처음 보는 문장"을 시험하는 것이 아니므로, 문장을 먼저 나눕니다.
#
#    시험 문장은 통째로 학습에 넣지 않되, 단어와 패턴은 다른 문장에서
#    이미 본 조합으로 고릅니다. 신경망이 의미 구조를 옮겨 쓰는지 보기 위해서입니다.
#    예: 학습에 Die Katze schläft, ... jagt die Maus
#        → 시험의 Die Maus schläft 를 행위자-서술어로 읽을 수 있는지
# ---------------------------------------------------------------------------
check_sentences(SENTENCES)

train_sents = SENTENCES
TEST_SENTS = [
    (["Die", "Maus", "schläft", "."],
     ["AGT", "AGT", "PRED", "O"]),
    (["Der", "Mann", "liest", "ein", "Buch", "."],
     ["AGT", "AGT", "PRED", "PAT", "PAT", "O"]),
    (["Das", "kleine", "Kind", "spielt", "."],
     ["AGT", "AGT", "AGT", "PRED", "O"]),
    (["Die", "Katze", "schläft", "gern", "."],
     ["AGT", "AGT", "PRED", "MNR", "O"]),
    (["Der", "Hund", "sitzt", "im", "Garten", "."],
     ["AGT", "AGT", "PRED", "LOC", "LOC", "O"]),
    (["Die", "Frau", "hat", "ein", "Buch", "gelesen", "."],
     ["AGT", "AGT", "O", "PAT", "PAT", "PRED", "O"]),
    (["Der", "alte", "Hund", "schläft", "."],
     ["AGT", "AGT", "AGT", "PRED", "O"]),
    (["Die", "Übung", "ist", "schön", "."],
     ["THM", "THM", "PRED", "ATTR", "O"]),
    (["Das", "Kind", "gibt", "der", "Frau", "Brot", "."],
     ["AGT", "AGT", "PRED", "REC", "REC", "PAT", "O"]),
    (["Der", "Brief", "wird", "gelesen", "."],
     ["PAT", "PAT", "O", "PRED", "O"]),
]
check_sentences(TEST_SENTS)
test_sents = TEST_SENTS

# 변환표는 학습 문장의 단어만으로 만듭니다.
word_to_id = build_word_vocab([s[0] for s in train_sents])

# 의미역 이름도 번호로 바꿉니다. 신경망의 출력 칸 하나가 종류 하나에 해당합니다.
role_names = sorted({tag for _tokens, tags in train_sents for tag in tags})
role_to_id = {name: i for i, name in enumerate(role_names)}
id_to_role = {i: name for name, i in role_to_id.items()}

X_win, y_role = make_dataset(train_sents, word_to_id, role_to_id)

print("학습 문장 수:", len(train_sents), "/ 시험 문장 수:", len(test_sents))
print("단어 종류 수(PAD/UNK 포함):", len(word_to_id))
print("의미역 종류:", ", ".join(role_names))
print("학습 단어 샘플 수:", len(y_role))
print()


# ---------------------------------------------------------------------------
# 4) 의미역 신경망
#
#    02강 벡터: 사람이 횟수를 세어 만든 값
#    여기 임베딩: 학습이 스스로 찾는 작은 단어 벡터
#                 같은 역할의 단어(관사 Der/Die/Das, 동사 schläft/liest)가
#                 비슷한 숫자를 갖게 됩니다.
#
#    구조: 창의 각 단어 → 임베딩 → 이어 붙임 → 은닉층 → 의미역 점수
#    04강의 형태소 태거와 같고, 단위만 글자에서 단어로 바뀌었습니다.
# ---------------------------------------------------------------------------
class SemParser(nn.Module):
    """주변 단어를 보고 한 단어의 의미역을 예측하는 작은 신경망입니다."""

    def __init__(self, vocab_size, n_roles, emb_dim=24, hidden=64, window_size=2 * WINDOW + 1):
        super().__init__()
        # 단어 번호 → 길이 24짜리 벡터. 이 숫자들은 학습하면서 바뀝니다.
        self.emb = nn.Embedding(vocab_size, emb_dim)
        # 창이 7단어이면 7 * 24 = 168차원이 은닉층으로 들어갑니다.
        self.hidden = nn.Linear(emb_dim * window_size, hidden)
        self.out = nn.Linear(hidden, n_roles)

    def forward(self, window_ids):
        # window_ids 모양: (샘플 수, 창 길이)
        # 임베딩 후 모양: (샘플 수, 창 길이, 24) → 한 줄로 펼침
        vectors = self.emb(window_ids)
        flat = vectors.reshape(window_ids.size(0), -1)
        # relu: 음수는 0으로 만들어, 03강의 다층 신경망처럼 굽은 경계를 그릴 수 있게 합니다.
        hidden = torch.relu(self.hidden(flat))
        return self.out(hidden)


parser = SemParser(
    vocab_size=len(word_to_id),
    n_roles=len(role_names),
)

# 텐서: 파이토치가 기울기(얼마나 고칠지)를 계산할 수 있는 숫자 묶음
X_win_t = torch.tensor(X_win)
y_role_t = torch.tensor(y_role)

# CrossEntropyLoss: 정답 칸의 점수는 높이고, 다른 칸의 점수는 낮추도록 차이를 재는 함수
# Adam: 그 차이를 줄이는 방향으로 가중치를 조금씩 수정하는 최적화 방법
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(parser.parameters(), lr=0.01)

n_epochs = 180
for epoch in range(1, n_epochs + 1):
    parser.train()
    scores = parser(X_win_t)            # 각 의미역에 대한 점수
    loss = loss_fn(scores, y_role_t)    # 정답과 얼마나 다른지
    optimizer.zero_grad()               # 직전 반복의 수정량을 지움
    loss.backward()                     # 각 가중치를 어느 쪽으로 고칠지 계산
    optimizer.step()                    # 실제로 조금 수정
    if epoch in (1, 45, 90, 135, 180):
        print(f"학습 {epoch:3d}번째, 손실(작을수록 좋음): {loss.item():.3f}")


def predict_tags(tokens):
    """한 문장의 각 단어에 대해 의미역 태그를 예측합니다."""
    parser.eval()
    windows = np.array(
        [window_to_ids(word_window(tokens, i), word_to_id) for i in range(len(tokens))],
        dtype=np.int64,
    )
    with torch.no_grad():  # 예측만 할 때는 수정량 계산이 필요 없습니다.
        role_ids = parser(torch.tensor(windows)).argmax(dim=1).numpy()
    return [id_to_role[int(i)] for i in role_ids]


# ---------------------------------------------------------------------------
# 5) 평가
#
#    단어 정확도: 단어마다 태그가 맞는 비율
#    구(스팬) 정확도: 이어 붙인 의미역 구가 정답과 완전히 같은 문장의 비율
#    서술어 정확도: PRED 위치를 맞힌 비율
#
#    실제 의미역 분석에서는 F1(정밀도·재현율의 조화평균)을 많이 씁니다.
#    여기서는 초보자가 읽기 쉬운 비율만 보여 줍니다.
# ---------------------------------------------------------------------------
def collect_eval(sentences):
    gold_tags, pred_tags = [], []
    gold_spans, pred_spans = [], []
    gold_pred, pred_pred = [], []
    for tokens, tags in sentences:
        predicted = predict_tags(tokens)
        gold_tags.extend(tags)
        pred_tags.extend(predicted)
        gold_spans.append(tags_to_spans(tokens, tags))
        pred_spans.append(tags_to_spans(tokens, predicted))
        gold_pred.extend([t == "PRED" for t in tags])
        pred_pred.extend([t == "PRED" for t in predicted])
    return gold_tags, pred_tags, gold_spans, pred_spans, gold_pred, pred_pred


g_tags, p_tags, g_spans, p_spans, g_pred, p_pred = collect_eval(test_sents)
span_exact = np.mean([a == b for a, b in zip(g_spans, p_spans)])
print("시험 단어 의미역 정확도:", round(accuracy_score(g_tags, p_tags), 3))
print("시험 문장 구(논리식) 완전 일치:", round(float(span_exact), 3))
print("서술어(PRED) 위치 정확도:", round(accuracy_score(g_pred, p_pred), 3))
print()


def print_conll(tokens, tags, gold_tags=None):
    """한 문장을 표로 보여 줍니다. 정답이 있으면 맞음(O)/틀림(X)도 적습니다."""
    print(f"{'번호':<4} {'단어':<14} {'의미역':<16}", end="")
    if gold_tags is not None:
        print(f" {'정답':<16} 판정")
    else:
        print()
    print("-" * (40 if gold_tags is None else 60))
    for i, token in enumerate(tokens):
        line = f"{i + 1:<4} {token:<14} {format_role(tags[i]):<16}"
        if gold_tags is not None:
            ok = "O" if tags[i] == gold_tags[i] else "X"
            line += f" {format_role(gold_tags[i]):<16} {ok}"
        print(line)


def print_frame(spans):
    """서술어를 뿌리로, 나머지를 가지로 보여 줍니다."""
    preds = [(role, text) for role, text in spans if role == "PRED"]
    args = [(role, text) for role, text in spans if role != "PRED"]
    if not preds:
        print("(서술어를 찾지 못했습니다)")
        return
    print(f"{format_role('PRED')}: {preds[0][1]}")
    for i, (role, text) in enumerate(args):
        branch = "└─ " if i == len(args) - 1 else "├─ "
        print(branch + f"{format_role(role)}: {text}")


def print_qa(spans):
    """의미역을 '누가? / 무엇을?' 같은 질문으로 풀어 줍니다."""
    for role, text in spans:
        question = ROLE_QA.get(role, role)
        print(f"  {question:12} {text}")


print("시험 문장 분석 (O=맞음, X=틀림)")
for tokens, tags in test_sents:
    predicted = predict_tags(tokens)
    spans = tags_to_spans(tokens, predicted)
    print()
    print("문장:", " ".join(tokens))
    print_conll(tokens, predicted, gold_tags=tags)
    print("의미 구조:")
    print_frame(spans)
    print("논리식:", format_logic(spans))
    print("질문으로 풀기:")
    print_qa(spans)
print()


# ---------------------------------------------------------------------------
# 6) 한 문장을 단계별로 풀어 보기
#    초보자가 "단어 → 창 → 의미역 → 구 → 논리식" 순서를 따라갈 수 있게
#    중간 결과를 출력합니다.
# ---------------------------------------------------------------------------
demo_tokens = ["Der", "Hund", "jagt", "die", "Katze", "."]
demo_tags = predict_tags(demo_tokens)
demo_spans = tags_to_spans(demo_tokens, demo_tags)
print("단계별 예시:", " ".join(demo_tokens))
print(f"{'위치':<4} {'단어':<8} {'창(주변 단어)':<45} {'의미역'}")
print("-" * 80)
for i, tok in enumerate(demo_tokens):
    window_txt = " ".join(word_window(demo_tokens, i))
    print(f"{i:<4} {tok:<8} {window_txt:<45} {format_role(demo_tags[i])}")
print()
print("구로 합치기:")
for role, text in demo_spans:
    print(f"  {format_role(role):<16} {text}")
print("논리식:", format_logic(demo_spans))
print()


# ---------------------------------------------------------------------------
# 7) 통사 주어와 의미역이 갈라지는 장면
#    같은 "문장 앞쪽 명사 구"가 능동에서는 행위자, 수동에서는 대상,
#    계사 문장에서는 테마가 됩니다. 05강 nsubj 만으로는 이 차이가 안 보입니다.
# ---------------------------------------------------------------------------
print("통사 주어 ≠ 의미 역할 비교")
print(f"{'문장':<42} {'앞쪽 명사구':<16} {'의미역'}")
print("-" * 78)
for text in [
    "Der Hund schläft .",
    "Der Brief wird geschrieben .",
    "Die Blume ist schön .",
]:
    tokens = text.split()
    tags = predict_tags(tokens)
    spans = tags_to_spans(tokens, tags)
    first = spans[0] if spans else ("?", "?")
    print(f"{text:<42} {first[1]:<16} {format_role(first[0])}")
print()


# ---------------------------------------------------------------------------
# 8) 새 문장 분석
#    학습에 넣은 문장과, 비슷한 뼈대를 가진 새 문장을 함께 넣어 봅니다.
#    아래 리스트를 바꿔 가며 실행해 보세요.
# ---------------------------------------------------------------------------
print("참고용 분석 (정답 없이 모델 예측만)")
for text in [
    "Der Hund schläft .",
    "Die Lehrerin erklärt die Übung .",
    "Kleine Kinder spielen im Garten .",
    "Der junge Student hat ein Buch gelesen .",
    "Die Lehrerin gibt dem Kind das Buch .",
    "Das Buch wird gelesen .",
]:
    tokens = text.split()
    tags = predict_tags(tokens)
    spans = tags_to_spans(tokens, tags)
    print()
    print("문장:", text)
    print_conll(tokens, tags)
    print("의미 구조:")
    print_frame(spans)
    print("논리식:", format_logic(spans))
print()


# ---------------------------------------------------------------------------
# 9) 의미역 구간 시각화
#    단어를 가로로 놓고, 같은 역할의 구를 색 상자로 묶습니다.
#    상자 위에 역할 이름을 쓰고, 제목에 논리식을 적습니다.
# ---------------------------------------------------------------------------
ROLE_COLORS = {
    "PRED": "#264653",
    "AGT": "#2a9d8f",
    "PAT": "#e76f51",
    "REC": "#4c6ef5",
    "THM": "#6d597a",
    "ATTR": "#e9c46a",
    "LOC": "#b56576",
    "TMP": "#f4a261",
    "MNR": "#8ab17d",
    "NEG": "#9d0208",
    "O": "#cccccc",
}


def draw_sentence(ax, tokens, tags, title):
    """한 문장의 의미역 상자를 한 칸의 그래프에 그립니다."""
    n = len(tokens)
    ax.set_xlim(-0.55, n - 0.45)
    ax.set_ylim(-0.45, 1.35)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11)

    i = 0
    while i < n:
        j = i
        # O 가 아닌 같은 태그가 이어지면 한 상자로 묶습니다.
        if tags[i] != "O":
            while j + 1 < n and tags[j + 1] == tags[i]:
                j += 1
            color = ROLE_COLORS.get(tags[i], "#333333")
            width = (j - i + 1) - 0.16
            box = FancyBboxPatch(
                (i - 0.42, 0.18),
                width,
                0.72,
                boxstyle="round,pad=0.04,rounding_size=0.08",
                facecolor=color,
                edgecolor=color,
                alpha=0.22,
                linewidth=1.2,
            )
            ax.add_patch(box)
            ax.text(
                (i + j) / 2,
                1.05,
                tags[i],
                ha="center",
                va="bottom",
                fontsize=8,
                color=color,
            )
        i = j + 1

    for k, tok in enumerate(tokens):
        ax.text(k, 0.52, tok, ha="center", va="center", fontsize=11)


show_sents = [
    "Der Hund jagt die Katze .",
    "Die Kinder spielen im Garten .",
    "Die Lehrerin gibt dem Kind das Buch .",
    "Die Blume ist schön .",
    "Der Brief wird geschrieben .",
    "Der Student hat ein Buch gelesen .",
]

fig, axes = plt.subplots(len(show_sents), 1, figsize=(11, 2.15 * len(show_sents)))
if len(show_sents) == 1:
    axes = [axes]
for ax, text in zip(axes, show_sents):
    tokens = text.split()
    tags = predict_tags(tokens)
    logic = format_logic(tags_to_spans(tokens, tags))
    draw_sentence(ax, tokens, tags, logic)

legend_roles = ("PRED", "AGT", "PAT", "REC", "THM", "ATTR", "LOC", "MNR")
handles = [
    Patch(facecolor=ROLE_COLORS[name], edgecolor="none", alpha=0.55,
          label=f"{name} ({ROLE_KO[name]})")
    for name in legend_roles
]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False)
plt.tight_layout(rect=(0, 0.06, 1, 1))
plt.show()
