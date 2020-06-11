import csv

asdf = []

with open('krwordrank_example.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        asdf.append(row)

#print(amen)

amen = [row_element for row in asdf for row_element in row]
#print(amen)

texts = [
    amen[0],
    amen[1],
    amen[2],
    amen[3],
    amen[4],
    amen[5],
    amen[6]
]
'''
from krwordrank.word import KRWordRank

min_count = 1 # 단어의 최소 출현 빈도수 (그래프 생성 시)
max_length = 10 # 단어의 최대 길이
wordrank_extractor = KRWordRank(min_count, max_length, verbose=True)
beta = 0.85 # PageRank의 decaying factor beta
max_iter = 10

keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)

for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
    print('%8s:\t%.4f' % (word, r))

'''

'''
from krwordrank.sentence import summarize_with_sentences

#keywords, sents = summarize_with_sentences(texts, num_keywords=100, num_keysents=10)

penalty=lambda x:0 if (15 <= len(x) <= 80) else 1

keywords, sents = summarize_with_sentences(
    texts, penalty=penalty,
    diversity=0.5,
    num_keywords=100,
    num_keysents=2,
    verbose=False
)
print(keywords)
print(sents)
'''


from krwordrank.word import KRWordRank

#texts = [] # Comments about 'La La Land (2016)'
wordrank_extractor = KRWordRank(min_count=5, max_length=10)
keywords, rank, graph = wordrank_extractor.extract(texts, num_keywords=20)
print(keywords)
