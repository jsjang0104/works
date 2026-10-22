"""05. WordNet/유사 의미망 기반 탐색

어휘 간의 의미 관계를 그래프로 표현합니다.
Bank가 'Geldinstitut'(금융)과 'Sitzbank'(벤치)로
갈라지는 구조를 한눈에 볼 수 있습니다.
"""

import networkx as nx
import matplotlib.pyplot as plt

# 무방향 그래프 생성 (의미망의 간단한 모형)
G = nx.Graph()

# (상위/중심 개념, 관련 개념) 형태의 의미 관계
relations = [
    ("Bank", "Geldinstitut"),   # Bank → 금융기관 의미
    ("Bank", "Sitzbank"),       # Bank → 벤치 의미
    ("Geldinstitut", "Kredit"), # 금융기관과 관련된 개념
    ("Sitzbank", "Park"),       # 벤치와 관련된 장소
]
G.add_edges_from(relations)

# spring_layout: 연결된 노드끼리 가깝게 배치
plt.figure(figsize=(7, 5))
pos = nx.spring_layout(G, seed=42)  # seed로 배치 결과 고정
nx.draw(G, pos, with_labels=True, node_color="#cfe8ff", node_size=2500, font_size=10)
plt.title("의미망 기반 어휘 탐색")
plt.tight_layout()
plt.show()
