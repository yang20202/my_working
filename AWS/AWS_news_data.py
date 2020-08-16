import urllib3
import json
import ast
import re
import csv
import datetime
import decimal
import boto3
from collections import OrderedDict
# from boto3.s3.transfer import S3Transfer

# APIkey
ApiURL =
accessKey =
# access_key는 교체 필요
aws_access_key_id =
aws_secret_access_key =

# 어제 뉴스 데이터 수집
yesterday = datetime.date.today() - datetime.timedelta(1)
today_convert = datetime.date.today().strftime('%Y-%m-%d')
yesterday_convert = yesterday.strftime('%Y-%m-%d')

providers_id = {'경향신문': '1', '국민일보': '2', '내일신문': '3', '동아일보': '4', '문화일보': '5', '서울신문': '6', '세계일보': '7', '조선일보': '8',
                '중앙일보': '9', '한겨례': '10', '한국일보': '11', '매일경제': '12', '머니투데이': '13', '서울경제': '14', '아시아경제': '15',
                '아주경제': '16', '파이낸셜뉴스': '17', '한국경제': '18', '헤럴드경제': '19', '강원도민일보': '20', '강원일보': '21', '경기일보': '22',
                '경남도민일보': '23', '경남신문': '24', '경상일보': '25', '경인일보': '26', '광주매일신문': '27', '광주일보': '28', '국제신문': '29',
                '대구일보': '30', '대전일보': '31', '매일신문': '32', '무등일보': '33', '부산일보': '34', '영남일보': '35', '울산매일': '36',
                '전남일보': '37', '전북도민일보': '38', '전북일보': '39', '제민일보': '40', '중도일보': '41', '중부매일': '42', '중부일보': '43',
                '충북일보': '44', '충청일보': '45', '충청투데이': '46', '한라일보': '47', 'KBS': '48', 'MBC': '49', 'OBS': '50',
                'SBS': '51', 'YTN': '52', '디지털타임스': '53', '전자신문': '54'}


def lambda_handler(event, context):
    # 몇개의 뉴스를 가져올 것인지
    news_num = 3000
    query = ''
    start_date = yesterday_convert
    end_date = today_convert
    category = ''

    # 뉴스검색 API
    requestJson = {
        "access_key": accessKey,
        "argument": {
            "query": query,
            "published_at": {
                "from": start_date,
                "until": end_date
            },
            "provider": {
                ""
            },
            "category": [
                category
            ],
            "category_incident": [
                ''
            ],
            "byline": "",
            "provider_subject": [
                ''
            ],
            "subject_info": [
                ""
            ],
            "subject_info1": [
                ""
            ],
            "subject_info2": [
                ""
            ],
            "subject_info3": [
                ""
            ],
            "subject_info4": [
                ""
            ],
            "sort": {"date": "asc"},
            "return_from": 0,
            # 몇개를 가져올 것인가
            "return_size": news_num,
            "fields": [
                'news_id',
                'title',
                'content',
                'published_at',
                'enveloped_at',
                'dateline',
                'provider',
                "category",
                "category_incident",
                'hilight',
                "byline",
                'images',
                'provider_subject',
                'subject_info',
                'subject_info1',
                'subject_info2',
                'subject_info3',
                'subject_info4',
                'provider_news_id',
                'publisher_code',
                'provider_link_page',
                'printing_page'
            ]
        }
    }

    # 소수점 에러를 피하기위해서
    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, set):
                return list(o)
            if isinstance(o, decimal.Decimal):
                if o % 1 > 0:
                    return float(o)
                else:
                    return int(o)
            return super(DecimalEncoder, self).default(o)

    http = urllib3.PoolManager()
    response = http.request(
        'POST',
        ApiURL,
        headers={'Content-Type': 'application/json; charset=UTF-8'},
        body=json.dumps(requestJson, cls=DecimalEncoder)
    )

    all_data = response.data.decode('utf-8')
    # 분석 가능하게 형태변환
    data = ast.literal_eval(all_data)
    return_object = data['return_object']
    documents = return_object['documents']

    # 항상 있을때
    def make_row1(column_name):
        file_data[column_name] = documents[i][column_name]

    # 없는경우를 고려
    def make_row2(column_name):
        try:
            file_data[column_name] = documents[i][column_name]
        except Exception:
            file_data[column_name] = ''

    # 본문에 이메일 있으면 가져오기 위해서
    def email_Reg(content):
        email = []
        emailReg = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))')
        try:
            email = emailReg.search(content).group(0)
        except Exception:
            pass
        return email

    for i in range(len(documents)):
        file_data = OrderedDict()

        make_row1('news_id')
        make_row1('title')
        make_row1('content')
        make_row1('published_at')
        make_row1('enveloped_at')
        make_row1('dateline')
        make_row1('provider')
        make_row1('category')
        make_row1('category_incident')
        make_row1('byline')
        make_row1('images')
        make_row2('provider_subject')
        make_row1('provider_news_id')
        make_row1('publisher_code')
        make_row1('provider_link_page')
        make_row1('printing_page')
        make_row2('subject_info')
        make_row2('subject_info1')
        make_row2('subject_info2')
        make_row2('subject_info3')
        make_row2('subject_info4')
        file_data['reporter_email'] = email_Reg(documents[i]['content'])

        with open('/tmp/%s_%s.json' % (start_date, i + 1), 'w', encoding='utf-8') as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent='\t')

        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        bucket_name = 'factagora-news'

        provider_id = providers_id[documents[i]['provider']]
        year = yesterday_convert[:4]
        month = yesterday_convert[5:7]
        date = yesterday_convert
        file_name = documents[i]['news_id']

        time = datetime.datetime.now().strftime('%H_%M_%S')

        s3.upload_file('/tmp/%s_%s.json' % (start_date, i + 1), bucket_name,
                       'provider=%s/yr=%s/mo=%s/dt=%s/%s.json' % (provider_id, year, month, date, file_name))
        # s3.upload_file('/tmp/%s_%s.json' % (start_date, i+1), bucket_name, 'amen/%s_%s.json' % (file_name, time))

        # transfer = S3Transfer(s3)
        # transfer.upload_file('/tmp/%s_%s.json' % (start_date, i+1), bucket_name, 'amen/%s_%s.json' % (file_name, time))
