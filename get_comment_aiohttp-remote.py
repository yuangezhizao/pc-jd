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
import asyncio
import aiohttp
import aiomysql
import json
import re
import pymysql
import datetime

#解析文本，返回评论列表[[], [], []]，第page页的txt
def parse(txt, page):
    comment_dict = json.loads(txt[26:-2]) #comment dictionary
    #max page
    max_page = comment_dict['maxPage'] #该sku的评论页数
    #comment summary
    comment_summary = comment_dict['productCommentSummary']
    good_count = comment_summary.get('goodCount', 0)
    general_count = comment_summary.get('generalCount', 0)
    poor_count = comment_summary.get('poorCount', 0)
    #image count
    image_list_count = comment_dict.get('imageListCount', 0) #该SKU评论中的图片数量
    #comments
    comments = comment_dict['comments']
    comment_list = []
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
            comment_i = [good_count,general_count,poor_count,image_list_count,max_page,page,
                         comment_id,comment_guid,comment_content,creation_time,
                         reference_time,reference_id,reference_name,first_category,
                         second_category,third_category,reply_count,score,status_code,
                         title,useful_vote_count,useless_vote_count,user_image_url,
                         user_level_id,user_province,user_register_time,nickname,
                         user_client,product_color,product_size,image_count,anonymous_flag,
                         user_level_name,user_client_show,days]
            comment_list.append(comment_i)
            #return comment_i
    return comment_list
                  
#爬取sku的第i页评论，并存入数据库
async def get_comment_i(sku, i):
    url = 'http://club.jd.com/comment/skuProductPageComments.action?productId=%s&score=0&sortType=3&page=%s&pageSize=10&callback=fetchJSON_comment98vv4914'%(sku,i)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            txt = await response.text()
            comments = parse(txt, i)
            crawl_date = datetime.datetime.today()
            now = datetime.datetime.now()
            crawl_time = now.strftime('%H:%M:%S')
            if len(comments)>0: #评论非空
                for comment in comments:
                    comment = [crawl_id, sku]+comment+[crawl_date, crawl_time]
                    conn = await aiomysql.connect(host='192.168.1.105', user='commen', password='1111', db='customer', charset='utf8')
                    cur = await conn.cursor()
                    sql = 'insert into comment_jd(crawl_id,sku,good_count,general_count,\
                           poor_count,image_list_count,max_page,page,comment_id,comment_guid,comment_content,\
                           creation_time,reference_time,reference_id,reference_name,\
                           first_category,second_category,third_category,reply_count,score,\
                           status_code,title,useful_vote_count,useless_vote_count,user_image_url,\
                           user_level_id,user_province,user_register_time,nickname,user_client,\
                           product_color,product_size,image_count,anonymous_flag,user_level_name,\
                           user_client_show,days,crawl_date,crawl_time) values(%s,%s,%s,%s,\
                           %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
                           %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                    await cur.execute(sql, comment)
                    await conn.commit()
                    await cur.close()
                    conn.close()
            else:
                pass

#限制并发数量
async def bound_fetch(sem, sku, i):
    async with sem:
        await get_comment_i(sku,i)
                    
#爬取sku的所有评论，从start_page页开始     
def get_comment(sku, start_page):
    url = 'http://club.jd.com/comment/skuProductPageComments.action?productId=%s&score=0&sortType=3&page=0&pageSize=10&callback=fetchJSON_comment98vv4914'%sku
    response = requests.get(url)
    txt = response.text
    comment_dict = json.loads(txt[26:-2]) #comment dictionary
    #max page
    max_page = comment_dict['maxPage'] #该sku的评论页数
    print(max_page)
    if max_page>0: #若页数为0，会出现ValueError: Set of coroutines/Futures is empty.
        loop = asyncio.get_event_loop()
        tasks = []
        sem = asyncio.Semaphore(15) #并发数量15
        for i in range(start_page, max_page): #从start_page开始
            task = asyncio.ensure_future(bound_fetch(sem, sku, i))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))      
    else:
        pass

#获得待抓取的sku：{sku:开始页数}，crawl_id是sku_jd的抓取编号，category_level3_id待抓取类别
def get_skus(crawl_id, category_level3_id):
    skus = {}
    conn = pymysql.connect(host='192.168.1.105', user='commen', password='1111', db='customer')
    cur = conn.cursor()
    #读取该品类的所有SKU
    sku_all=[]
    sql_all = 'select distinct sku from sku_jd where crawl_id="%s" and \
               category_level3_id="%s"'%(crawl_id, category_level3_id)
    cur.execute(sql_all)
    for i in cur.fetchall():
        for j in i:
            sku_all.append(j)
    #读取该品类已被抓取的SKU
    sku_crawled = []
    sql_crawled = 'select distinct sku from comment_jd where \
                   concat(first_category, ",", second_category, ",", third_category)\
                   ="%s"'%category_level3_id
    cur.execute(sql_crawled)
    for i in cur.fetchall():
        for j in i:
            sku_crawled.append(j)
    #未爬取的sku
    sku_not_crawled = [i for i in sku_all if i not in sku_crawled]
    #读取可能未爬完的sku，由于是并发，最后一条的记录可能不是最大的
    sql_latest = 'select sku,max_page,max(page)\
                  from( \
                  select sku,max_page,page from comment_jd \
                  where concat(first_category, ",", second_category, ",", third_category)="%s"\
                  order by id desc limit 100) a\
                  group by sku'%category_level3_id
    cur.execute(sql_latest)
    r = cur.fetchall()
    if len(r):
        for i in r:
            sku_latest = i[0] #未爬完的sku
            max_page_latest = i[1] #该sku的评论页数
            page_latest = i[2] #已爬到的页数
            if page_latest < max_page_latest:
                skus[sku_latest] = page_latest+1
    cur.close()
    conn.close()
    #未爬取sku的初始页数
    for sku in sku_not_crawled:
        skus[sku] = 0
    return skus

if __name__ == '__main__':
    global crawl_id
    crawl_id = input('输入抓取编号（201611）：')
    crawl_id_sku_jd = input('请选择待抓取sku的抓取编号（sku_jd中）：')
    category_level3_id = input('请输入待抓取的商品类别编码：')
    skus = get_skus(crawl_id_sku_jd, category_level3_id)
    for sku in skus:
        get_comment(sku, skus[sku])

