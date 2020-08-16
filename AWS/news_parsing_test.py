import boto3
import json
import re
from konlpy.tag import Okt
import json
from collections import OrderedDict

aws_access_key_id =
aws_secret_access_key =

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

bucket_name =
object_name = 'provider=16/yr=2020/mo=06/dt=2020-06-13'

paginator = s3.get_paginator('list_objects_v2')

response_iterator = paginator.paginate(
    Bucket=bucket_name,
    Prefix='provider=16/yr=2020/mo=06/dt=2020-06-13'
)
print(paginator)

s3_1 = boto3.resource(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

files_content = []
files_name = []
datelines = []

for page in response_iterator:
    for content in page['Contents']:
        content_object = s3_1.Object(bucket_name, content['Key'])
        file_content = content_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        # 기사 id
        file_name = json_content['news_id']
        # 기사 내용
        content = json_content['content']
        # 기사 작성 날짜
        dateline = json_content['dateline']
        files_content.append(content)
        files_name.append(file_name)
        datelines.append(dateline)

okt = Okt()
# ex) 슬기는
whos = re.compile('[가-힣]+[는|은]')
# ex) 사람이름이 길 경우 ex) 박 장관은
whos2 = re.compile('[가-힣]+ [가-힣]+[은|는]')
texts = re.compile('“.+”')
date1 = re.compile('')

# 전체 파일 다 돌게 만들어야한다.
for m, file_content in enumerate(files_content):
    # 각 기사의 전체 문장 개수
    word_length = len(file_content)
    # 뉴스 id
    file_name = files_name[m]
    # 뉴스 작성 시간 및 날짜
    dateline = datelines[m]
    sentences = []
    sentence_start = 0
    # .을 기준으로 문장 구분하기
    for i in range(word_length):
        if file_content[i] == '.':
            if i != word_length - 1:
                if file_content[i + 1] == '"':
                    continue
            sentences.append(file_content[sentence_start: i + 1])
            sentence_start = i + 1

    file_data = OrderedDict()
    file_data['news_id'] = file_name
    file_data['dateline'] = dateline

    for n, sentence in enumerate(sentences):
        # " 가 있는 문장만 가져온다
        if '“' in sentence:
            # text가 아예 없는 경우 고려
            try:
                text = texts.search(sentence).group(0)
            except:
                continue
            # long_name이 없을 경우도 있기 때문에
            try:
                long_name = whos2.search(sentence).group(0)
                morphs = okt.pos(long_name)
                if len(morphs) >= 3:
                    # 만약 단어들 안에 조사가 있으면 사람이름이 아닌것이다 ex) 지지만 실천은
                    for i in range(len(morphs)-1):
                        if morphs[i][1] == 'Josa':
                            continue
                    # 마지막 형태소는 조사, 첫단어랑 중간단어는 명사인 경우만
                    if morphs[len(morphs) - 1][1] == 'Josa' and morphs[0][1] == 'Noun' and morphs[len(morphs) - 2][1] == 'Noun':
                        # 이름이 "" 안에 있으면 파싱 실패한 것이기 때문에
                        if long_name in text:
                            continue

                        print("문장: ", sentence)
                        print("이름: ", long_name[:-1])
                        print("말: ", text)
                        print('---------------------')
                        # 해당 문장이 몇 번째 문장인지에 따라 parsed_result 뒤에 %s 붙였음
                        file_data['parsed_result_%s' % n] = {'person': long_name[:-1]}
                        file_data['quotes_%s' % n] = text
                        with open('%s_parsed.json' % file_name, 'w', encoding='utf-8') as make_file:
                            json.dump(file_data, make_file, ensure_ascii=False, indent='\t')

                        continue
            except:
                pass
            # name이 없을 경우도 있기때문에
            try:
                name = whos.search(sentence).group(0)

                # 단어들 품사구별
                morphs = okt.pos(name)
                # 형태소가 하나인 단어들은 제외 ex) 최소 대통령+은 과같이 형태소가 2개여야함
                if len(morphs) >= 2:
                    # 마지막 형태소가 조사일때만
                    if morphs[len(morphs) - 1][1] == 'Josa':
                        # 첫 형태소가 명사일때만
                        try:
                            okt.nouns(name)[0]
                            # 이름이 "" 안에 있으면 파싱 실패한 것이기 때문에
                            if name in text:
                                continue
                            print("문장: ", sentence)
                            print("이름: ", name[:-1])
                            print("말: ", text)
                            print('---------------------')

                            # 해당 문장이 몇 번째 문장인지에 따라 parsed_result 뒤에 %s 붙였음
                            file_data['parsed_result_%s' % n] = {'person': name[:-1]}
                            file_data['quotes_%s' % n] = text
                            with open('%s_parsed.json' % file_name, 'w', encoding='utf-8') as make_file:
                                json.dump(file_data, make_file, ensure_ascii=False, indent='\t')

                        except:
                            continue
            except:
                pass
