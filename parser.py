from unittest import result
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxOptions


import pandas as pd
import numpy as np
import math
import json
import matplotlib.pyplot as plt
import seaborn as sns
import time
import re
from bs4 import BeautifulSoup

json_file = 'temp.json'
write_file = 'result.txt'
result_dict = {}

class LenError(Exception):
    def __str__(self):
        return "length does not match"

def get_comments(browser):
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    total_comment_number = 0
    
    try:
        total_comment_number = int(soup.find(class_='total_evaluation').find(class_='color_b').get_text())
    except:
        total_comment_number = 0
    
    try:
        evaluation_list = soup.find(class_='list_evaluation').find_all('li', recursive=False)
    except:
        return [], [], []
    
    #
    
    s = [x.find(class_='inner_star')['style'] for x in evaluation_list]
    l = [x.find_all(class_='chip_likepoint') for x in evaluation_list]
    c = [x.find(class_='txt_comment').find('span') if x.find(class_='txt_comment') else None for x in evaluation_list]

    
    star = [int(re.findall(r'\d+', x)[0]) / 20 if x else None for x in s]
    comment = [x.get_text() if x else None for x in c]
    #likepoint = [for x in l for y in x]
    likepoint = []
    for x in l:
        temp = []
        for y in x:
            temp.append(y.get_text())
        likepoint.append(temp)
    #likepoint = [x.get_text() if x else None for y in l for x in y]

    # for 문을 순회하면서 평가를 수집한다.
    
    print(star, likepoint, comment)
    if not len(star) == len(likepoint) == len(comment) == total_comment_number: 
        raise LenError
    return star, likepoint, comment

def scroll(browser):
    last_height = browser.execute_script("return document.body.scrollHeight")
    count = 0
    while True:
        # 스크롤 아래로 내리기
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 스크롤 다운 후 스크롤 높이 다시 가져옴
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"scrolling {count}")
        count+=1
        # 리뷰 더보기 버튼 클릭하기
        try:
            txt_more = browser.find_element(By.CLASS_NAME, 'txt_more')
            html = browser.page_source
            soup = BeautifulSoup(html, 'lxml')
            txt_more.click()
            if soup.find(class_='link_unfold'):# 마지막에 다다르면 끈다.
                break
            if soup.find(class_='box_grade_off'):# 리뷰가 제공되지 않는 매장이라면 off
                break
            # http://place.map.kakao.com/1507185592 이거 해결해야함
            if count > 50: # 임시로 해놓음;; 원인을 못찾겠다
                break
        except:
            break

def one_store_analyze(store_data, browser, f):
    '''
    한 가게의 정보를 받으면 해당 정보를 바탕으로 댓글을 추출하는 함수다.
    
    store_data(dictionary) : 가게의 정보가 담긴 dictionary 
    browser 셀레니움 드라이버
    '''

    # url 을 초기화 
    # https://place.map.kakao.com/20000829 언플러그드 신촌
    # https://place.map.kakao.com/8122805 클로리스
    url = store_data['place_url']
    #url = 'http://place.map.kakao.com/606314892'
    print(url)
    # url에서 정보를 가져온다.
    

    browser.get(url)
    
    # 스크롤 하기
    scroll(browser)
    print("scroll complete")
    # 이제 beautiful soup으로 html 가져오기
    star, likepoint, comment = get_comments(browser)

    # 댓글 담고 있는 li tag만 추출 recursive=False로 설정
    # 전체 댓글과 LEN 비교해서 만약에 len 이 맞지 않으면 경고 report 하기
    print(store_data['place_name'], star, likepoint, comment, file=f)

    return []

def read_result_dict():
    global result_dict
    try:
        with open(json_file, 'r') as temp:
            result_dict = json.load(temp)   
    except:
        print('file read error')
        exit(1)

if __name__ == '__main__':
    webdriver_service = Service('/usr/bin/geckodriver')

    opts = FirefoxOptions()
    opts.add_argument("--headless")		# turn off GUI
    browser = webdriver.Firefox(service=webdriver_service, options=opts)

    doc = {
      "address_name": "서울 서대문구 대현동 27-33",
      "category_group_code": "CE7",
      "category_group_name": "카페",
      "category_name": "음식점 > 카페 > 테마카페 > 디저트카페",
      "distance": "138",
      "id": "577825774",
      "phone": "02-363-9222",
      "place_name": "그릭데이 이대점",
      "place_url": "http://place.map.kakao.com/577825774",
      "road_address_name": "서울 서대문구 신촌역로 22-8",
      "x": "126.94335642719437",
      "y": "37.55884593416747"
    }
    read_result_dict()
    f = open(write_file, 'w')
    
    #one_store_analyze(doc, browser, f)

    # 이미 json은 중복 제거 했고
    print(f'read {len(result_dict["documents"])} stores')
    
    for i in result_dict['documents']:
        one_store_analyze(i, browser, f)

