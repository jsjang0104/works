# ==============================================================================
# 1. 필요한 library import
# ==============================================================================
# import
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import time
import re
import random
from collections import Counter
import math
import matplotlib.pyplot as plt
import numpy as np
import shutil
import os

from transformers import GPT2Tokenizer
from torchtext.datasets import AG_NEWS  # AG_NEWS: 뉴스 기사 텍스트 분류 데이터셋
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

# ==============================================================================
# 2. Experiment Setup
# ==============================================================================
# GPU 사용 가능 여부 확인 및 장치 설정 (Colab GPU 사용)
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"CUDA is available. Using device: {device}")
else:
    device = torch.device("cpu")
    print(f"CUDA not available. Using device: {device}")

# 하이퍼파라미터 설정
EMBEDDING_DIM = 100  # embedding dimension
WINDOW_SIZE = 10  # context window size
NUM_NEGATIVES = 5  # negative sampling
LEARNING_RATE = 0.025  # learning rate
BATCH_SIZE = 1024  # batch size
NUM_EPOCHS = 15  # epoch
MIN_FREQ = 10  # minimun frequency

# ==============================================================================
# 3. Data Processing
# ==============================================================================
# 0. 깨진 파일 문제 해결용
cache_path = "/root/.cache/torch/text/datasets/AG_NEWS"

if os.path.exists(cache_path):
    print(f"깨진 데이터 캐시 발견! 삭제 중... : {cache_path}")
    shutil.rmtree(cache_path)
    print("삭제 완료. 깨끗한 상태에서 다시 다운로드를 시작합니다.")
else:
    print("ℹ기존 캐시가 없습니다. 바로 다운로드를 시작합니다.")


# 1. 데이터셋 로드 및 토큰화 ---------------------------------------------------
tokenizer = get_tokenizer("basic_english")
train_iter = AG_NEWS(split="train")
print("코퍼스 로드 및 토큰화 중... (기본 토크나이저 적용)")

tokenized_corpus = []
for label, line in train_iter:
    if len(line) > 0:
        tokens = tokenizer(line)
        tokenized_corpus.extend(tokens)
print(f"로드된 초기 토큰 수: {len(tokenized_corpus)}")


# 2. Vocabulary Building and filtering -----------------------------------------
word_counts = Counter(tokenized_corpus)  # 빈도수 계산
vocab = sorted(
    [word for word, count in word_counts.items() if count >= MIN_FREQ]
)  # 최소 빈도수 이상의 단어만 포함하여 어휘집 구축
vocab.insert(0, "<unk>")  # OOV (Out-Of-Vocabulary) 특수 토큰

word_to_ix = {word: i for i, word in enumerate(vocab)}  # 단어 -> 인덱스 맵핑
ix_to_word = {i: word for i, word in enumerate(vocab)}  # 인덱스 -> 단어 맵핑
VOCAB_SIZE = len(vocab)
print(f"최소 빈도 {MIN_FREQ} 적용 후 어휘집 크기 (VOCAB_SIZE): {VOCAB_SIZE}")


# 3. 코퍼스 정제 및 subsampling ---------------------------------------------
unk_idx = word_to_ix["<unk>"]
indexed_corpus = [word_to_ix.get(w, unk_idx) for w in tokenized_corpus]

# Subsampling 확률 계산 (frequent words dropping)
total_count = sum(word_counts.values())
word_freqs = {w: c / total_count for w, c in word_counts.items()}
# subsampling probability: P(w) = 1 - sqrt(t / f(w)), t=1e-5 usually
t = 1e-5
drop_probs = {
    word_to_ix[w]: 1 - np.sqrt(t / (word_freqs[w] + 1e-10))
    for w in vocab
    if w in word_counts
}

# 훈련 데이터 생성 (Subsampling 적용하여 미리 필터링) -> 메모리 절약 및 속도 향상
# <unk>와 자주 등장하는 단어를 확률적으로 제거한 최종 리스트 생성
train_data_indices = []
for idx in indexed_corpus:
    if idx == unk_idx:
        continue
    # Subsampling: 확률적으로 drop
    if idx in drop_probs and random.random() < drop_probs[idx]:
        continue
    train_data_indices.append(idx)

print(
    f"Original Size: {len(indexed_corpus)} -> Subsampled Size: {len(train_data_indices)}"
)

# Negative Sampling Weights
counts_tensor = torch.tensor(
    [word_counts[ix_to_word[i]] for i in range(VOCAB_SIZE)], dtype=torch.float
)
neg_weights = counts_tensor**0.75
neg_weights = neg_weights / neg_weights.sum()


# 5. PyTorch Dataset 클래스 정의 -----------------------------------------------
class Word2VecDataset(Dataset):
    def __init__(self, data_indices, window_size):
        self.data = data_indices
        self.window_size = window_size

    def __len__(self):
        # 끝부분 window 처리를 위해 길이 조정
        return len(self.data) - (2 * self.window_size)

    def __getitem__(self, idx):
        # 실제 인덱스는 window_size 만큼 밀려서 시작
        actual_idx = idx + self.window_size

        center_word = self.data[actual_idx]

        # Dynamic Window: 1 ~ WINDOW_SIZE 사이 랜덤 축소 (Word2Vec 트릭)
        current_window = random.randint(1, self.window_size)

        # Context Window 범위 설정
        context_start = max(0, actual_idx - current_window)
        context_end = min(len(self.data), actual_idx + current_window + 1)

        context_words = (
            self.data[context_start:actual_idx]
            + self.data[actual_idx + 1 : context_end]
        )

        # 하나만 랜덤 선택 (SGD 효율성)
        if len(context_words) > 0:
            pos_word = random.choice(context_words)
        else:
            # 문맥이 없는 경우(드물지만) 자기 자신 혹은 다음 단어 대체
            pos_word = self.data[min(len(self.data) - 1, actual_idx + 1)]

        return torch.tensor(center_word, dtype=torch.long), torch.tensor(
            pos_word, dtype=torch.long
        )


# Collate_fn에서 Negative Sampling 수행 (GPU 활용 극대화 및 CPU 부하 분산)
def collate_fn(batch):
    centers, pos_contexts = zip(*batch)
    centers = torch.stack(centers)
    pos_contexts = torch.stack(pos_contexts)

    # Negative Sampling (Batch 단위로 한 번에 수행하여 속도 향상)
    neg_contexts = torch.multinomial(
        neg_weights, len(batch) * NUM_NEGATIVES, replacement=True
    )
    neg_contexts = neg_contexts.view(len(batch), NUM_NEGATIVES)

    return centers, pos_contexts, neg_contexts


dataset = Word2VecDataset(train_data_indices, WINDOW_SIZE)
dataloader = DataLoader(
    dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn, num_workers=2
)


# ==============================================================================
# 4. Model Definition (Skip-gram with Negative Sampling Model)
# ==============================================================================
class SkipGram(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super().__init__()
        self.center_embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.context_embeddings = nn.Embedding(vocab_size, embedding_dim)

        # 초기화 수정: 작은 범위로 설정
        initrange = 0.5 / embedding_dim
        self.center_embeddings.weight.data.uniform_(-initrange, initrange)
        self.context_embeddings.weight.data.uniform_(-initrange, initrange)

    def forward(self, center, pos, neg):
        # (B, D)
        v = self.center_embeddings(center)
        # (B, D)
        u_pos = self.context_embeddings(pos)
        # (B, K, D)
        u_neg = self.context_embeddings(neg)

        # Positive Score: (B, 1, D) @ (B, D, 1) -> (B, 1) -> (B)
        pos_score = torch.bmm(v.unsqueeze(1), u_pos.unsqueeze(2)).squeeze()

        # Negative Score: (B, 1, D) @ (B, D, K) -> (B, K)
        # transpose(1, 2) -> (B, D, K)
        neg_score = torch.bmm(v.unsqueeze(1), u_neg.transpose(1, 2)).squeeze(1)

        return pos_score, neg_score


# ==============================================================================
# 5. Training Loop
# ==============================================================================

model = SkipGram(VOCAB_SIZE, EMBEDDING_DIM).to(device)
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.LinearLR(
    optimizer,
    start_factor=1.0,
    end_factor=0.01,
    total_iters=NUM_EPOCHS * len(dataloader),
)  # 학습률 스케줄러: 학습이 진행될수록 LR을 줄여서 미세 조정
criterion = nn.BCEWithLogitsLoss()
loss_history = []  # Loss 기록용 리스트

print("\n--- Training Start ---")
for epoch in range(NUM_EPOCHS):
    total_loss = 0
    model.train()
    start = time.time()

    for i, (center, pos, neg) in enumerate(dataloader):
        center, pos, neg = center.to(device), pos.to(device), neg.to(device)

        optimizer.zero_grad()
        pos_score, neg_score = model(center, pos, neg)

        # Loss
        pos_targets = torch.ones_like(pos_score)
        neg_targets = torch.zeros_like(neg_score)

        loss = criterion(pos_score, pos_targets) + criterion(neg_score, neg_targets)

        loss.backward()
        optimizer.step()
        scheduler.step()  # 스텝마다 학습률 감소

        total_loss += loss.item()

        if i % 500 == 0 and i > 0:
            print(
                f"Epoch {epoch+1} | Step {i}/{len(dataloader)} | Loss: {loss.item():.4f}"
            )
    avg_loss = total_loss / len(dataloader)
    loss_history.append(avg_loss)

    print(
        f"Epoch {epoch+1} Done. Avg Loss: {total_loss/len(dataloader):.4f} | Time: {time.time()-start:.1f}s"
    )


# ==============================================================================
# 6. Loss Visualization
# ==============================================================================
plt.figure(figsize=(10, 5))
plt.plot(loss_history, marker="o", linestyle="-", color="b", label="Training Loss")
plt.title("Word2Vec Training Loss (AG_NEWS)")
plt.xlabel("Epoch")
plt.ylabel("Average Loss")
plt.grid(True)
plt.legend()
plt.show()


# ==============================================================================
# 7. Evaluation
# ==============================================================================
embeddings = model.center_embeddings.weight.data.cpu().numpy()


# cosine similarity
def get_most_similar(word, top_k=5):
    if word not in word_to_ix:
        print(f"'{word}' is not in vocabulary.")
        return

    vec = embeddings[word_to_ix[word]]

    norms = np.linalg.norm(embeddings, axis=1)
    vec_norm = np.linalg.norm(vec)
    sims = np.dot(embeddings, vec) / (norms * vec_norm + 1e-8)

    # 정렬
    indices = np.argsort(sims)[::-1]

    print(f"\n[Query] {word}")
    count = 0
    for idx in indices:
        if idx == word_to_ix[word] or ix_to_word[idx] == "<unk>":
            continue
        print(f"  - {ix_to_word[idx]}: {sims[idx]:.4f}")
        count += 1
        if count >= top_k:
            break


# word analogy
def analogy(a, b, c):
    if any(w not in word_to_ix for w in [a, b, c]):
        print(f"Words not in vocab: {[w for w in [a,b,c] if w not in word_to_ix]}")
        return

    va, vb, vc = (
        embeddings[word_to_ix[a]],
        embeddings[word_to_ix[b]],
        embeddings[word_to_ix[c]],
    )
    target = vb - va + vc

    norms = np.linalg.norm(embeddings, axis=1)
    target_norm = np.linalg.norm(target)
    sims = np.dot(embeddings, target) / (norms * target_norm + 1e-8)

    indices = np.argsort(sims)[::-1]
    print(f"\n[Analogy] {a}:{b} = {c}:?")
    count = 0
    seen = {a, b, c, "<unk>"}
    for idx in indices:
        word = ix_to_word[idx]
        if word in seen:
            continue
        print(f"  -> {word} ({sims[idx]:.4f})")
        count += 1
        if count >= 3:
            break


# 테스트 실행 (데이터셋 특성 반영)
test_words = ["microsoft", "football", "president", "war"]
for w in test_words:
    get_most_similar(w)
analogy("china", "beijing", "japan")  # 예상: tokyo
analogy("france", "paris", "germany")  # 예상: berlin # Classic
analogy("microsoft", "software", "intel")  # 예상: chips, hardware
get_most_similar("cpu")
get_most_similar("gold")

print("\n=== 최종 검증: 데이터셋(뉴스) 맞춤형 테스트 ===")

# 1. 테크 기업 라이벌 관계
# Microsoft : Windows = Google : ? (예상: Search, Yahoo 등)
analogy("microsoft", "windows", "google")
get_most_similar("internet")

# 2. 스포츠
# Swimming : Phelps = Cycling : ? (예상: Armstrong(당시 아주 유명했던 사이클링 선수))
analogy("swimming", "phelps", "cycling")
get_most_similar("medal")
