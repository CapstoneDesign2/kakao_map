from unittest import result
import requests
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

def get_comments(response):
    '''
    api 가 들어있는 url 이다.
    만약에 response['comment']['hasNext'] 값이 False라면 
    response['comment']를 return 아니라면 hasNext값이 False가 될 때까지 loop를 돌면서 
    https://place.map.kakao.com/commentlist/v/(가게 id)/(마지막 comment 의 comment_id)
    '''
    print(f"response has next {response['comment']['hasNext']}")
    
    # 만약에 hasNext가 false라면 원래 값을 return 해준다.
    if not response['comment']['hasNext']:
        return

    # dictionary의 마지막 index
    last_idx = 0
    
    #while loop 을 돌면서 response['commnet']['list']에 값을 추가하는 방식
    while True:
        # 항상 2번 key값이 마지막이다.
        # 맨 마지막 key 값을 return 하게 한다.
        #https://stackoverflow.com/questions/16125229/last-key-in-python-dictionary
        last_comment = response['comment']['list'][-1]
        last_idx = list(response['comment']['list'])[-1]

        #print(last_idx)
        #print(last_comment)
        
        last_comment_id = last_comment['commentid']
        store_id = response['basicInfo']['cid']
        
        print(f'last comment id is : {last_comment_id} store id is : {store_id}')
        
        # 새로운 comment를 받아줄 url이다.
        comment_retrive_url = f'https://place.map.kakao.com/commentlist/v/{store_id}/{last_comment_id}'
        
        comment_response = requests.get(comment_retrive_url).json()
        
        # 여기서 나온 댓글을 새로 목록에 추가한다.
        #print(comment_response)
        
        # expend 해주기
        response['comment']['list'].extend(comment_response['comment']['list'])

        if not comment_response['comment']['hasNext']:
            break
        


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

def one_store_analyze(store_data):
    '''
    한 가게의 정보를 받으면 해당 정보를 바탕으로 댓글을 추출하는 함수다.
    
    store_data(dictionary) : 가게의 정보가 담긴 dictionary 
    browser 셀레니움 드라이버
    '''

    # url 을 초기화 
    # https://place.map.kakao.com/20000829 언플러그드 신촌
    # https://place.map.kakao.com/8122805 클로리스
    store_data['place_url'] = 'http://place.map.kakao.com/606314892'
    store_data['id'] = 606314892

    url = store_data['place_url']
    store_id = store_data['id']
    #https://place.map.kakao.com/main/v/884526216
    print(url)
    # url에서 정보를 가져온다.
    
    info_url = f'https://place.map.kakao.com/main/v/{store_id}'
    # basicInfo의 feedback은 댓글나열한거
    # s2 graph가 매장의 정보를 나열한거
    
    # get_commnet 에서 댓글 가져오기 json 형식
    # [comment][list]에 0, 1, 2 추가하는 방식
    response = requests.get(info_url).json()
    get_comments(response)
    
    print(response['comment']['list'])
    print(len(response['comment']['list']))

def read_result_dict():
    global result_dict
    try:
        with open(json_file, 'r') as temp:
            result_dict = json.load(temp)   
    except:
        print('file read error')
        exit(1)

if __name__ == '__main__':
    
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
    #read_result_dict()
    #f = open(write_file, 'w')
    
    #one_store_analyze(doc, browser, f)

    # 이미 json은 중복 제거 했고
    #print(f'read {len(result_dict["documents"])} stores')
    
    #for i in result_dict['documents']:
    #    one_store_analyze(i, browser, f)
    one_store_analyze(doc)
