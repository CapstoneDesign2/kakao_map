from unittest import result
import requests
import pymysql
import sqlalchemy as db
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from db_class import StoreClass, CommentClass, STORE_TABLE_NAME, COMMENT_TABLE_NAME
from db_configure import *


import pandas as pd
import numpy as np
import math
import json
import matplotlib.pyplot as plt
import seaborn as sns
import time
import re
from bs4 import BeautifulSoup

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
    #print(f"response has next {response['comment']['hasNext']}")

    # 만약에 hasNext가 false라면 원래 값을 return 해준다.

    #while loop 을 돌면서 response['commnet']['list']에 값을 추가하는 방식
    while response['comment']['hasNext']:
        # 항상 2번 key값이 마지막이다.
        # 맨 마지막 key 값을 return 하게 한다.
        #https://stackoverflow.com/questions/16125229/last-key-in-python-dictionary
        last_comment = response['comment']['list'][-1]
        
        last_comment_id = last_comment['commentid']
        store_id = response['basicInfo']['cid']
        
        #print(f'last comment id is : {last_comment_id} store id is : {store_id}')
        
        # 새로운 comment를 받아줄 url이다.
        comment_retrive_url = f'https://place.map.kakao.com/commentlist/v/{store_id}/{last_comment_id}'
        
        comment_response = requests.get(comment_retrive_url).json()
        
        # 여기서 나온 댓글을 새로 목록에 추가한다.
        #print(comment_response)
        
        # expend 해주기
        response['comment']['list'].extend(comment_response['comment']['list'])
        # hasNext를 comment_response 의 hasNext로 바꿔준다.
        response['comment']['hasNext'] = comment_response['comment']['hasNext']        

def one_store_analyze(store_id):
    
    info_url = f'https://place.map.kakao.com/main/v/{store_id}'
    
    # basicInfo의 feedback은 댓글나열한거
    # s2 graph가 매장의 정보를 나열한거
    print(info_url)
    response = requests.get(info_url).json()

    # 만약에 comment라는 key 값이 없으면 그냥 return
    if 'comment' not in response.keys() or 'list' not in response['comment'].keys():
        print('리뷰 엥꼬~')
        return

    # get_commnet 에서 댓글 가져오기 json 형식
    get_comments(response)
    #print(response)
    
    ## comment 디비에 저장
    for comment in response['comment']['list']:
        # datetime 형식으로 바꾸는게 낫겠지?
        #print(f"comment {comment.get('contents')}")
        #print(f"comment {comment.get('username')}")
        # 문자열 없거나 길이 초과시 대처법
        comment_final = ""
        comment_temp = comment.get('contents')
        
        if not comment_temp:
            comment_final = ""
        elif len(comment_temp) > 512:
            comment_final = comment_temp[:510]
        else:
            comment_final = comment_temp
        
        store = CommentClass(
                             comment['commentid'],  
                             comment_final,
                             comment['point'],
                             comment['photoCnt'], 
                             comment['likeCnt'],
                             comment['kakaoMapUserId'],
                             comment.get('username'),
                             photoList="",
                             strengths="",
                             userCommentCount=comment['userCommentCount'],
                             userCommentAverageScore=comment['userCommentAverageScore'],
                             date=comment['date'],
                             store_id=store_id
                            )
        session.add(store)
        
    session.commit()
    ## comment 디비에 저장

    #print(response['comment']['list'])
    #print(len(response['comment']['list']))

def read_store_from_database():
    
    stmt = db.select(StoreClass)
    # store 의 id 모음
    ret = [x.id for x in session.scalars(stmt)]    
    
    return ret

def comment_db_control():
    engine.execute(f'DELETE FROM {COMMENT_TABLE_NAME}')

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
    
    engine = db.create_engine(f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{database}')
    Session = sessionmaker(engine)
    session = Session() # 이거로 orm 통제
    
    store_id_list = read_store_from_database()
    #print(store_id_list)
    #exit()
    
    comment_db_control()
    
    #one_store_analyze(763496937)
    #comment.get('contents'),
    for id in store_id_list:
        one_store_analyze(id)
    
    #one_store_analyze(doc)
    
