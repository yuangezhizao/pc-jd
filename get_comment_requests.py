# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 09:29:44 2016
get comment content
1. 相关SKU的所有评论
http://sclub.jd.com/comment/productPageComments.action?productId=1427585&score=0&sortType=3&page=0&pageSize=10&callback=fetchJSON_comment98vv4914

2. 指定SKU的评论
http://club.jd.com/comment/skuProductPageComments.action?productId=1427585&score=0&sortType=3&page=0&pageSize=10&callback=fetchJSON_comment98vv4914
@author: Administrator
"""
import requests
import json
import re
import pymysql
import datetime
import pandas as pd

def parse(sku):
    url = 'http://club.jd.com/comment/skuProductPageComments.action?productId=%s&score=0&sortType=3&page=0&pageSize=10&callback=fetchJSON_comment98vv4914'%sku
    response = requests.get(url)
    txt = response.text
    comment_dict = json.loads(txt[26:-2]) #comment dictionary
    #comment summary
    comment_summary = comment_dict['productCommentSummary']
    good_count = comment_summary.get('goodCount', 0)
    general_count = comment_summary.get('generalCount', 0)
    poor_count = comment_summary.get('poorCount', 0)
    #max page
    max_page = comment_dict['maxPage']
    #image count
    image_list_count = comment_dict['imageListCount'] #该SKU评论中的图片数量
    for i in range(0, max_page+1):
        comment_list = []
        url_i = 'http://club.jd.com/comment/skuProductPageComments.action?productId=%s&score=0&sortType=3&page=%s&pageSize=10&callback=fetchJSON_comment98vv4914'%(sku,i)
        try:        
            response_i = requests.get(url_i)
        except:
            continue
        txt_i = response_i.text
        comment_dict_i = json.loads(txt_i[26:-2])
        #comments
        comments = comment_dict_i['comments']
        crawl_date = datetime.date.today()
        now = datetime.datetime.now()
        crawl_time = now.strftime('%H:%M:%S')
        if len(comments) > 0:
            for i in range(0, len(comments)):
                comment = comments[i]
                comment_id = str(comment.get('id', ''))
                comment_guid = comment.get('guid', '')
                comment_content = comment.get('content', '') #评论内容
                creation_time = comment.get('creationTime', '') #评论创建时间
                reference_time = comment.get('referenceTime', '') #基准时间，顾客收货时间
                #is_top = comment.get('isTop', '')
                reference_id = comment.get('referenceId', '') #基准sku
                reference_name = comment.get('referenceName', '')
                first_category = str(comment.get('firstCategory', ''))
                second_category = str(comment.get('secondCategory', ''))
                third_category = str(comment.get('thirdCategory', ''))
                reply_count = comment.get('replyCount', 0)
                score = comment.get('score', 0)
                status_code = str(comment.get('status', ''))
                title = comment.get('title', '')
                useful_vote_count = comment.get('usefulVoteCount', 0) #点赞数量
                useless_vote_count = comment.get('uselessVoteCount', 0)
                user_image_url = comment.get('userImageUrl', '') #头像url
                user_level_id = comment.get('userLevelId', '')
                user_province = comment.get('userProvince', '') #省份
                user_register_time = comment.get('userRegisterTime', '') #注册时间
                nickname = comment.get('nickname', '') 
                user_client = str(comment.get('userClient', ''))
                product_color = comment.get('productColor', '')
                product_size = comment.get('productSize', '')
                image_count = comment.get('imageCount', 0) #该条评论中图片数量
                anonymous_flag = str(comment.get('anonymousFlag', '')) #匿名标志
                user_level_name = comment.get('userLevelName', '') #会员级别
                if len(comment.get('userClientShow', '')): #设备来源
                    user_client_show = re.findall('(?<=>).+(?=<)', comment.get('userClientShow', ''))[0]
                else:
                    user_client_show=''
                #is_mobile = comment.get('isMobile', '')
                days = comment.get('days', 0)
                comment_list = [crawl_id,sku,good_count,general_count,poor_count,image_list_count,
                                comment_id,comment_guid,comment_content,creation_time,
                                reference_time,reference_id,reference_name,first_category,
                                second_category,third_category,reply_count,score,status_code,
                                title,useful_vote_count,useless_vote_count,user_image_url,
                                user_level_id,user_province,user_register_time,nickname,
                                user_client,product_color,product_size,image_count,anonymous_flag,
                                user_level_name,user_client_show,days,crawl_date,crawl_time]
                conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer', charset='utf8')
                cur = conn.cursor()
                sql = 'insert into comment_jd(crawl_id,sku,good_count,general_count,\
                poor_count,image_list_count,comment_id,comment_guid,comment_content,\
                creation_time,reference_time,reference_id,reference_name,\
                first_category,second_category,third_category,reply_count,score,\
                status_code,title,useful_vote_count,useless_vote_count,user_image_url,\
                user_level_id,user_province,user_register_time,nickname,user_client,\
                product_color,product_size,image_count,anonymous_flag,user_level_name,\
                user_client_show,days,crawl_date,crawl_time) values(%s,%s,%s,%s,\
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
                %s,%s,%s,%s,%s,%s,%s,%s,%s)'
                try:
                    cur.execute(sql, comment_list)
                    conn.commit()
                except:
                    continue
                cur.close()
                conn.close()

if __name__ == '__main__':
    global crawl_id
    crawl_id = input('输入抓取编号（201611）：')
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer')
    skus = pd.read_sql('select sku from sku_jd where crawl_id="201609" limit 1000000', conn)
    conn.close()
    skus = skus.drop_duplicates('sku')
    for sku in skus['sku']:
        try:
            parse(str(sku))
        except:
            print(sku)
            continue
