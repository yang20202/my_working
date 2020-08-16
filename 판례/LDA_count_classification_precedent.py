from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import json

okt = Okt()

# 페이지
page = 23
# 글 번호
writing_number = 51

title_list = []
list = []

# 페이지
for i in range(1, page + 1):
    # 글 번호
    for j in range(1, writing_number):
        with open('%s_%s.json' % (i, j), encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        title = json_data['title']

        if '유족' in title:
            if '급여' in title:
                try:
                            # 판시사항이 있다면
                    judgment = json_data['판시사항']

                    if len(judgment) >= 100:
                        list.append(judgment)
                    title = json_data['title']
                    title_list.append(title)
        #           list.append(judgment)
                except:
                    pass
print(len(title_list))
print(len(list))

content = pd.DataFrame(list, columns=['내용'])
# 생략하지 않고 보여주기
#pd.set_option('display.max_colwidth', -1)
#print(content)

def okt_morphs(text):
    morphs = okt.nouns(text)
    list = []
    for morph in morphs:
        if len(morph) > 1:
            list.append(morph)
    return list

# , ngram_range=(1, 2) stop_words=['대하', '대한',' 경우']
# 수집된 리뷰가 저장된 dataframe
stop_words = ['보험','보상','재해','대하', '대한', '경우', '사례','해당','소극','적극','여부']
tf_vect = CountVectorizer(tokenizer=okt_morphs,stop_words=['유족','급여','보험','근로자','업무','대하', '대한', '경우', '사례','해당','소극','적극','여부'], min_df=2, max_df=6000, max_features=25000)
#tf_vect = CountVectorizer(tokenizer=okt_morphs, stop_words=stop_words, min_df=2, max_df=6000, max_features=25000)
dtm = tf_vect.fit_transform(content['내용'])

# 주제 개수
n_topics = 5
# 주제에 포함된 단어 개수
n_words = 18

lda = LatentDirichletAllocation(n_components=n_topics, topic_word_prior=0.01, doc_topic_prior=0.001) # 0.001
lda.fit(dtm)

names = tf_vect.get_feature_names()
topics_word = dict()

# 주제에 속한 단어 topics_word 에 저장
for idx, topic in enumerate(lda.components_):
    vocab = []
    for i in topic.argsort()[:-(n_words-1):-1]:
        vocab.append((names[i], topic[i].round(2)))
    topics_word[idx+1] = [(names[i], topic[i].round(2)) for i in topic.argsort()[:-(n_words-1):-1]]

# 주제당 가장 큰 비중을 차지하는 리뷰 출력
max_dict = dict()
for idx, vec in enumerate(lda.transform(dtm)):
    # 토픽개수별 vector중 가장 큰 수
    t = vec.argmax()
    if t not in max_dict:
        max_dict[t] = (vec[t], idx, title_list[idx])
    else:
        if max_dict[t][0] < vec[t]:
            max_dict[t] = (vec[t], idx, title_list[idx])
subject_word = sorted(max_dict.items(), key=lambda x: x[0], reverse=False)
print(subject_word)

subject_dict = dict()
# 모든 내용들 주제별 매칭
for idx, vec in enumerate(lda.transform(dtm)):
    # 토픽개수별 vector 중 가장 큰 수
    t = vec.argmax()
    subject_dict[idx] = (vec[t], t)
all_review_subject = sorted(subject_dict.items(), key=lambda x: x[0], reverse=False)


# 주제별 키워드들
for key, value in subject_word:
    print('주제 {}: {}'.format(key+1, topics_word[key+1]))
    print('[주제 {}의 대표 리뷰 : 제목 : {} , 점수 : {}]\n내용 : \n{}\n\n'.format(key + 1, value[2], value[0], content['내용'][value[1]]))

# 모든 글의 주제 번호와 0~1까지의 점수
for key, value in all_review_subject:
    print('[ {}번째 글 : {}, 주제:{}, 점수:{}]\n{}\n\n'.format(key+1, title_list[key], value[1]+1, value[0], content['내용'][key]))


import pyLDAvis.sklearn
visual = pyLDAvis.sklearn.prepare(lda_model=lda, dtm=dtm, vectorizer=tf_vect)
pyLDAvis.save_html(visual, '유족급여_판결요지_topic_5_word_18_1.html')
#pyLDAvis.save_html(visual, '판시사항_n_topics=14_n_words=20_order=1.html')
pyLDAvis.display(visual)
