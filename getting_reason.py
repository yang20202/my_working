from selenium import webdriver as wd
import time
from krwordrank.sentence import summarize_with_sentences
# something change
options = wd.ChromeOptions()
# 크롬창 안보이게
options.add_argument('headless')
# 드라이버 로드
driver = wd.Chrome(executable_path='chromedriver.exe', options=options) #실행경로
# 크롤링을 오래돌리면 => 임시파일들이 쌓인다!! -> 템프 파일 삭제

main_url = 'https://glaw.scourt.go.kr/wsjo/intesrch/sjo022.do'
driver.get(main_url)
driver.implicitly_wait(5)
# 메뉴에 판례 클릭
driver.find_element_by_xpath('//li[@class="menu_2"]').click()

time.sleep(0.5)
# 화제의 판례 클릭
driver.find_element_by_xpath('//div[@class="sub_container"]/ul/li[1]').click()

#driver.find_element_by_xpath('//div[@class="tab_contents"]/div[id="treewrap"]/div[@class="tree"]/ul[@id="groupList"]/li[3]/ul/li[1]/a').click()
time.sleep(2)

# 각 판례들 클릭
for k in range(0, 7):
    driver.find_element_by_xpath('//tbody[@id="areaList"]/tr[@id="ln%s"]/td[2]/dl/dt/a[1]' % k).click()
    time.sleep(0.5)

    old_tab = driver.window_handles[0]
    new_tab = driver.window_handles[1]
    # 새로운 페이지로 전환
    driver.switch_to.window(new_tab)

    # 모든 문장의 개수
    all_texts = driver.find_elements_by_xpath('//div[@class="page_area"]/div[@class="page"]/p')
    p_length = len(all_texts)

    # JudgementNote가 P의 몇 번째인지 알 수 있나?

    JudgementNote_num = None
    RefLaw_num = None
    # 판결요지 시작순서
    for i in range(0, p_length):
        try:
            JudgementNote = driver.find_element_by_xpath('//div[@class="page_area"]/div[@class="page"]/p[%s]/strong[@id="JudgementNote"]' % i).text
            JudgementNote_num = i
#            print(JudgementNote_num)
            break
        except:
            pass
    # 참조조문 시작순서
    for i in range(0, p_length):
        try:
            RefLaw = driver.find_element_by_xpath('//div[@class="page_area"]/div[@class="page"]/p[%s]/strong[@id="RefLaw"]' % i).text
            RefLaw_num = i
#            print(RefLaw_num)
            break
        except:
            pass
    # 전체 판결요지 내용
    content = []

    for i in range(JudgementNote_num+1, RefLaw_num-1):
        JudgementNote = driver.find_element_by_xpath('//div[@class="page_area"]/div[@class="page"]/p[%s]' % i).text
        if JudgementNote != '':
            content.append(JudgementNote)

#    print(content)
#   print('---')
    # 한 문장 한 문장의 판결요지
    final_content = []
    # 전체 리스트 개수
    content_length = len(content)
    for i in range(0, content_length):
        # 리스트당 문자 개수
        word_length = len(content[i])
        sentence_start = 0
        # '.'를 기준으로 문장 나눠서 저장
        for j in range(0, word_length):
            if content[i][j] == '.':
                # 2019.4.5 같은경우 방지
                if content[i][j-1].isdigit():
                    continue
                # .가 문장 중간에 들어가 있고
                if j != word_length - 1:
                    # .”라고 전화고 있다 와 같은경우 방지 ( 판례 본문에서 직접 복사해와야한다.)
                    if content[i][j+1] == '”':
                        continue
                final_content.append(content[i][sentence_start:j+1])
                sentence_start = j+1

    print(k, '번째 글')
#    print(final_content)

#    from krwordrank.sentence import summarize_with_sentences

    penalty = lambda x: 0 if (15 <= len(x) <= 90) else 1

    keywords, sents = summarize_with_sentences(
        final_content, penalty=penalty,
        diversity=0.5,
        num_keywords=100,
        num_keysents=2,
        verbose=False
    )

    print(keywords)
    print(sents)

    driver.close()

    driver.switch_to.window(old_tab)

    print('----------------------------------')

driver.quit()

'''
from krwordrank.word import KRWordRank

min_count = 1 # 단어의 최소 출현 빈도수 (그래프 생성 시)
max_length = 10 # 단어의 최대 길이
wordrank_extractor = KRWordRank(min_count, max_length, verbose=True)
beta = 0.85 # PageRank의 decaying factor beta
max_iter = 10

keywords, rank, graph = wordrank_extractor.extract(final_content, beta, max_iter)

for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
    print('%8s:\t%.4f' % (word, r))
'''
'''
from krwordrank.sentence import summarize_with_sentences
penalty=lambda x:0 if (15 <= len(x) <= 90) else 1

keywords, sents = summarize_with_sentences(
    final_content, penalty=penalty,
    diversity=0.5,
    num_keywords=100,
    num_keysents=2,
    verbose=False
)

print(keywords)
print(sents)
'''

import sys
sys.exit()