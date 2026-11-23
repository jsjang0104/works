"""오분류 문장의 단어 빈도와 WordCloud를 생성합니다.

틀린 문장에 자주 나오는 단어를 보면, 모델이 어떤 어휘·주제에 약한지 가설을 세울 수 있습니다.
관사·조동사 같은 기능어는 제외하고 내용어 위주로 봅니다.
"""
from collections import Counter
import re
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 01에서 만든 평가용 CSV를 읽습니다. utf-8-sig는 엑셀에서 한글·움라우트가 깨지지 않게 합니다.
df = pd.read_csv('evaluation_data.csv', encoding='utf-8-sig')

# 오분류된 문장만 이어 붙여 하나의 텍스트로 만듭니다.
error_text = ' '.join(df.loc[df['true_label'] != df['pred_label'], 'text'].astype(str))
# 독일어 움라우트·ß를 포함한 단어만 추출하고 소문자로 통일합니다.
words = re.findall(r"[A-Za-zÄÖÜäöüß]+", error_text.lower())

# 빈도가 높아도 오류 원인 분석에 도움이 적은 기능어(불용어)를 제거합니다.
stopwords = {'der', 'die', 'das', 'ist', 'ich', 'mit', 'dem', 'den', 'ein', 'eine', 'und'}
words = [w for w in words if w not in stopwords and len(w) > 1]
freq = Counter(words)

print('=== 오분류 문장의 상위 단어 빈도 ===')
print(freq.most_common(15))
# 빈도표를 저장해 수업에서 엑셀·후속 분석으로 열어 볼 수 있게 합니다.
pd.DataFrame(freq.most_common(), columns=['word', 'frequency']).to_csv('error_word_frequency.csv', index=False, encoding='utf-8-sig')

if freq:
    # generate_from_frequencies: 이미 센 빈도를 그대로 반영합니다(원문 재토큰화 없음).
    cloud = WordCloud(width=900, height=450, background_color='white', colormap='viridis').generate_from_frequencies(freq)
    plt.figure(figsize=(12, 6))
    plt.imshow(cloud, interpolation='bilinear')
    plt.axis('off')  # 축은 단어구름에 필요 없으므로 숨깁니다.
    plt.title('WordCloud of Misclassified Texts')
    plt.tight_layout()
    plt.savefig('error_wordcloud.png', dpi=150)  # 12번 보고서에서 이 PNG 존재 여부를 확인합니다.
    plt.show()
else:
    print('오분류 텍스트가 없어 WordCloud를 생성하지 않았습니다.')
