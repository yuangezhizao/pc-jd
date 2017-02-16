# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 08:00:02 2016
一、功能
抓取category_level3_id-brand_id-sku_group各个评分的数量
二、逻辑
1.获取待抓取的任务category_level3_id-brand_id-sku_group
（1）获取待抓取的品类-品牌
（2）获取（1）中对应的sku_group
2.下载网页（http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=sku）
3.解析网页
4.存入数据库
三、禁爬规则
无

@author: Administrator
"""

import requests
import pymysql
import datetime
import pandas as pd

#获取爬取顺序，返回category_level3_id和数量
def get_category():
    category_level3_ids = []
    category = pd.read_csv('C:/Users/Administrator/Documents/GitHub/pc-jd/crawl_order.csv', 
                           encoding='gbk')
    category.sort_values(by='category_level3_order', inplace=True)
    for i in category['category_level3_id']:
        category_level3_ids.append(i.split('"')[1])
    n = len(category_level3_ids)
    return category_level3_ids, n

#获取待抓取的品牌-sku
def get_brand_sku(category_level3_id, crawl_id):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111',
                           db='customer', charset='utf8')
    #sku_jd所有的品牌-sku
    sku_all = []
    sql_all = 'select concat(brand_id, "-", sku_group) as sku\
               from sku_jd where crawl_id=(select crawl_id from sku_jd\
               order by id desc limit 1) and category_level3_id="%s"'\
               % category_level3_id #根据最新的crawl_id
    records_all = pd.read_sql(sql_all, conn)
    records_all = records_all.drop_duplicates('sku')
    for i in records_all['sku']:
        sku_all.append(i)
    #comment_count_jd已爬取的品牌-sku
    sku_crawled = []
    sql_crawled = 'select concat(brand_id, "-", sku_group) as sku\
                   from comment_count_jd where crawl_id=%s\
                   and category_level3_id="%s"' % (crawl_id, category_level3_id)
    records_crawled = pd.read_sql(sql_crawled, conn)
    records_crawled = records_crawled.drop_duplicates('sku')
    for i in records_crawled['sku']:
        sku_crawled.append(i)
    #未爬取的sku
    sku_task = [i for i in sku_all if i not in sku_crawled]
    sku_task.sort()
    n = len(sku_task)
    conn.close()
    return sku_task, n


#下载网页，成功返回文本，失败返回空文本，并打印错误
def load(sku_group):
    url = 'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=%s' % sku_group
    try:
        txt = requests.get(url).text
    except:
        print('get_comment_count-error-load: %s' % sku_group)
        txt = ''
    return txt

#解析网页，成功返回长度大于0的comments，失败返回长度为0的comments
def parse(sku_group, txt):
    try:
        crawl_date = datetime.date.today()
        now = datetime.datetime.now()
        crawl_time = now.strftime('%H:%M:%S')
        count_dict=eval(txt) #转换成字典
        score1_count=count_dict['CommentsCount'][0]['Score1Count']
        score2_count=count_dict['CommentsCount'][0]['Score2Count']
        score3_count=count_dict['CommentsCount'][0]['Score3Count']
        score4_count=count_dict['CommentsCount'][0]['Score4Count']
        score5_count=count_dict['CommentsCount'][0]['Score5Count']
        comment_count=count_dict['CommentsCount'][0]['CommentCount']
        comments = []
        comments = [score1_count, score2_count, score3_count, score4_count, 
                    score5_count, comment_count, crawl_date, crawl_time]
    except:
        print('get_comment_count-error-parse: %s' % sku_group)
        comments = [0, 0, 0, 0, 0, 0, crawl_date, crawl_time]       
    return comments

#存入mysql
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer')
    cur = conn.cursor()
    sql = 'insert into comment_count_jd(crawl_id, category_level3_id,\
           brand_id, sku_group, score1_count, score2_count, score3_count,\
           score4_count, score5_count, comment_count, crawl_date,\
           crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql, record)
        conn.commit()
        cur.close()
        conn.close()
    except:
        print('get_comment_count-error-input_mysql: %s' % record)
        cur.close()
        conn.close()
    
def crawl(crawl_id):
    category_level3_ids, n1 = get_category()
    if n1 > 0:
        for category_level3_id in category_level3_ids:
            brand_sku_list, n2 = get_brand_sku(category_level3_id, crawl_id)
            if n2 > 0:
                for brand_sku in brand_sku_list:
                    print('get_comment_count:已完成%s/%s品类，%s已完成%s/%s单品' %\
                    ((category_level3_ids.index(category_level3_id)+1), n1,\
                    category_level3_id, (brand_sku_list.index(brand_sku)+1), n2))
                    brand_id = brand_sku.split('-')[0]
                    sku_group = brand_sku.split('-')[1]
                    txt = load(sku_group)
                    if txt != '':
                        comments = parse(sku_group, txt)
                        record = [crawl_id, category_level3_id, brand_id, sku_group] + comments
                        input_mysql(record)
                        
            else:
                print('get_comment_count:%s已抓取完毕' % category_level3_id)
    else:
        print('get_comment_count:crawl_order中的品类已抓取完毕')  


if __name__=='__main__':
    crawl_id=input('请输入爬取编号：')
    crawl(crawl_id)
    

            
        
