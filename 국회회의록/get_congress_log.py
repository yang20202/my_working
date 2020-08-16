from selenium import webdriver as wd
import time
import json
from collections import OrderedDict

main_url = 'http://likms.assembly.go.kr/record/'
number_congress = 20

#options = wd.ChromeOptions()
# 크롬창 안보이게
#options.add_argument('headless') PDF 다운로드가 안 됨
# 드라이버 로드
driver = wd.Chrome(executable_path='chromedriver.exe') #실행경로
# 크롤링을 오래돌리면 => 임시파일들이 쌓인다!! -> 템프 파일 삭제

# 사이트 접속 (get)
driver.get(main_url)

# 전체회의록 클릭
driver.find_element_by_id('m03').click()
driver.implicitly_wait(5)
# 20대 국회 클릭
driver.find_element_by_css_selector('.highlighting').click()
time.sleep(0.5)

# case1 펼치고 요약정보 진입
def first_opening(html):
    num_title0 = driver.find_element_by_css_selector('.tabover').text
    print(num_title0)
    time.sleep(0.5)
    openings = driver.find_elements_by_css_selector(html)
    # ex) 제376회(2020.02.17~2020.03.17) 진입
    for opening in openings:
        num_title1 = opening.find_element_by_css_selector('.minutesLi>.close_wrap>a').text
        opening.find_element_by_css_selector('.minutesLi>.close_wrap>a').click()
        time.sleep(0.5)
        #num_title1 = opening.text
        print(num_title1)
        blocks = opening.find_elements_by_css_selector('.tree02>ul>li')
        # ex) 제5차(2020년03월02일) 진입
        for block in blocks:
            num_title2 = block.find_element_by_css_selector('span>a').text
            print(num_title2)
            # pdf 다운로드
            block.find_element_by_css_selector('span>.link>a>img[src="/record/res/img/sub/sub_pdf.gif"]').click()
            # 요약정보보기 클릭
            block.find_element_by_css_selector('a>img[alt="요약정보보기"]').click()
            time.sleep(0.5)
            # json 파일 이름
            file_name = num_title0 + '_' + num_title1 + '_' + num_title2
            file_data = OrderedDict()
            # 기존 화면 탭
            old_tab = driver.window_handles[0]
            time.sleep(0.5)
            # 요약정보 탭
            summarize_tab = driver.window_handles[1]
            # 요약정보 창으로 탭 전환
            driver.switch_to.window(summarize_tab)
            time.sleep(0.5)
            # 회의제목
            title()
            # 안건
            major_contents(file_data)
            # 출석자들
            attendees(file_data)
            # 동영상링크
            video_link(file_data)
            time.sleep(0.5)
            # 요약정보 창으로 복귀
            driver.switch_to.window(summarize_tab)
            # 요약정보 창 닫기
            driver.close()
            time.sleep(0.5)
            # 옛날 창으로 복귀
            driver.switch_to.window(old_tab)
            # 파일 생성
            with open('%s.json' % file_name, 'w', encoding='utf-8') as make_file:
                json.dump(file_data, make_file, ensure_ascii=False, indent='\t')


# case2 펼치고 요약정보 진입
def second_opening(html):
    num_title0 = driver.find_element_by_css_selector('.tabover').text
    print(num_title0)
    time.sleep(0.5)
    openings = driver.find_elements_by_css_selector(html)
    # ex)국회운영위원회 진입
    for opening in openings:
        num_title1 = opening.text
        opening.find_element_by_css_selector('.close_wrap>a').click()
        #opening.click()
        time.sleep(0.5)
        print(num_title1)
        blocks = opening.find_elements_by_css_selector('.open_wrap02>.tree01>ul>li')
        time.sleep(0.5)
        # ex) 제 371회 진입
        for block in blocks:
            num_title2 = block.find_element_by_xpath('//a[@href="#none"]').text
            #num_title2 = block.find_element_by_css_selector('a').text
            print(num_title2)
            time.sleep(0.5)
            block.find_element_by_css_selector('.first>a').click()
            sands = block.find_elements_by_css_selector('ul>li')
            # ex) 제2차(2019년 11월 29일) 진입
            for sand in sands:
                time.sleep(0.5)
                num_title3 = sand.find_element_by_css_selector('a').text
                print(num_title3)
                # pdf 다운로드
                sand.find_element_by_css_selector('span>.link>a>img[src="/record/res/img/sub/sub_pdf.png"]').click()
                # 요약정보보기 클릭
                sand.find_element_by_css_selector('a>img[alt="요약정보보기"]').click()
                time.sleep(0.5)
                # json 파일 이름
                file_name = num_title0 + '_' + num_title1 + '_' + num_title2 + '_' + num_title3
                file_data = OrderedDict()
                # 기존 화면 탭
                old_tab = driver.window_handles[0]
                time.sleep(0.5)
                # 요약정보 탭
                summarize_tab = driver.window_handles[1]
                # 요약정보 창으로 탭 전환
                driver.switch_to.window(summarize_tab)
                time.sleep(0.5)
                # 회의제목
                title()
                # 안건
                major_contents(file_data)
                # 출석자들
                attendees(file_data)
                # 동영상링크
                video_link(file_data)
                time.sleep(0.5)
                # 요약정보 창으로 복귀
                driver.switch_to.window(summarize_tab)
                # 요약정보 창 닫기
                driver.close()
                time.sleep(0.5)
                # 옛날 창으로 복귀
                driver.switch_to.window(old_tab)
                # 파일 생성
                with open('%s.json' % file_name, 'w', encoding='utf-8') as make_file:
                    json.dump(file_data, make_file, ensure_ascii=False, indent='\t')

# 회의제목
def title():
    title = driver.find_element_by_xpath("//div[@class='container_pop']/div[@class='content_pop']/h2[1]").text
    print(title)

# 안건
def major_contents(file_data):
    major_contents = driver.find_elements_by_css_selector('.content_pop>.popup_box>ul>li>div')
    total_major_content = []
    for major_content in major_contents:
        if major_content.text is not '':
            total_major_content.append(major_content.text)
    file_data["major_content"] = total_major_content

# 출석자들
def attendees(file_data):
    attendees = driver.find_elements_by_css_selector('.popup_box02>ul>li')
    total_attendees = []
    for attendee in attendees:
        total_attendees.append(attendee.text)
    print('\n')
    file_data["Attendees"] = total_attendees


# 동영상링크
def video_link(file_data):
    try:
        driver.find_element_by_xpath("//tbody/tr/td[2]/span/a").click()
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[2])
        time.sleep(0.5)
        video_link = driver.current_url
        file_data["video_link"] = video_link
        # 비디오 창 닫기
        driver.close()
    except Exception:
        file_data["video_link"]=[]
        print('\n')
        pass


# 국회본회의, 예산결산
def first_case(a, b):
    time.sleep(1)
    driver.execute_script('javascript:sesDegreeSubject_1(this, %s, %s)' % (a, b))
    time.sleep(0.5)
    # 펼치기
    first_opening('.con_minutes01>.minutesLi')
#first_opening('.minutesLi>.close_wrap>a')
# 상임위원회, 특별위원, 국정감사, 국정조사, 연석회의
def second_case(a, b):
    time.sleep(1)
    driver.execute_script('javascript:commSesDegreeSubject_1(this, %s, %s)' % (a, b))
    time.sleep(0.5)
    # 펼치기
    second_opening('.con_minutes01>.minutesLi')


# 국회본회의
#first_case(20, 1)
time.sleep(1)

# 예산결산특별위원회
#first_case(20, 4)
time.sleep(1)

# 상임위원회
second_case(20, 2)
time.sleep(1)

# 특별위원회
#second_case(20, 3)
time.sleep(1)

# 국정감사
#second_case(20, 5)
time.sleep(1)

# 국정조사
#second_case(20, 6)
time.sleep(1)

# 연석회의
#second_case(20, 12)
time.sleep(1)


driver.close()
driver.quit()
import sys
sys.exit()

