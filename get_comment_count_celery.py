# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 13:45:52 2016
一、功能
根据sku_jd.sku_group抓取京东SKU的评论数量，并存入数据库comment_count_jd
[id,crawl_id,sku,...,crawl_date,crawl_time]

二、逻辑
1.评论数量URL：http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=3243686

@author: thinkpad
"""

from celery import Celery
import pymysql
import requests
import datetime
import pandas as pd

app=Celery('get_comment_count_celery',broker='redis://localhost:6379')

@app.task
def get_comment_count(sku_group,crawl_id):
    url_base='http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds='
    url=url_base+str(sku_group)
    conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',
                         db='customer')
    cur=conn.cursor()
    try:
        response=requests.get(url).text
        count_dict=eval(response)
        score1_count=count_dict['CommentsCount'][0]['Score1Count']
        score2_count=count_dict['CommentsCount'][0]['Score2Count']
        score3_count=count_dict['CommentsCount'][0]['Score3Count']
        score4_count=count_dict['CommentsCount'][0]['Score4Count']
        score5_count=count_dict['CommentsCount'][0]['Score5Count']
        show_count=count_dict['CommentsCount'][0]['ShowCount']
        comment_count=count_dict['CommentsCount'][0]['CommentCount']
        average_score=count_dict['CommentsCount'][0]['AverageScore']
        good_count=count_dict['CommentsCount'][0]['GoodCount']
        good_rate=count_dict['CommentsCount'][0]['GoodRate']
        good_rate_show=count_dict['CommentsCount'][0]['GoodRateShow']
        good_rate_style=count_dict['CommentsCount'][0]['GoodRateStyle']
        general_count=count_dict['CommentsCount'][0]['GeneralCount']
        general_rate=count_dict['CommentsCount'][0]['GeneralRate']
        general_rate_show=count_dict['CommentsCount'][0]['GeneralRateShow']
        general_rate_style=count_dict['CommentsCount'][0]['GeneralRateStyle']
        poor_count=count_dict['CommentsCount'][0]['PoorCount']
        poor_rate=count_dict['CommentsCount'][0]['PoorRate']
        poor_rate_show=count_dict['CommentsCount'][0]['PoorRateShow']
        poor_rate_style=count_dict['CommentsCount'][0]['PoorRateStyle']
        crawl_date=datetime.date.today()
        now=datetime.datetime.now()
        crawl_time=now.strftime('%H:%M:%S')
        count=[crawl_id,sku_group,score1_count,score2_count,score3_count,
               score4_count,score5_count,show_count,comment_count,average_score,
               good_count,good_rate,good_rate_show,good_rate_style,
               general_count,general_rate,general_rate_show,general_rate_style,
               poor_count,poor_rate,poor_rate_show,poor_rate_style,
               crawl_date,crawl_time]
        sql='insert into comment_count_jd(crawl_id,sku_group,score1_count,\
        score2_count,score3_count,score4_count,score5_count,show_count,\
        comment_count,average_score,good_count,good_rate,good_rate_show,\
        good_rate_style,general_count,general_rate,general_rate_show,\
        general_rate_style,poor_count,poor_rate,poor_rate_show,poor_rate_style,\
        crawl_date,crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(sql,count)
        conn.commit()
        cur.close()
        conn.close()
    except:
        print('%s can not get comment count'%sku_group)
        cur.close()
        conn.close()

def query_sku_group(crawl_id):
    sku_group_list=[]
    conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',
                         db='customer')
    sql='select distinct sku_jd.sku_group from sku_jd where sku_jd.sku_group \
    not in (select comment_count_jd.sku_group from comment_count_jd where \
    comment_count_jd.crawl_id=%s)'%crawl_id
    sku_group_df=pd.read_sql(sql,conn)
    for sku_group in sku_group_df['sku_group']:
        sku_group_list.append(sku_group)
    conn.close()
    return sku_group_list

if __name__=='__main__':
    crawl_id=input('请输入爬取ID（201609）：')
    sku_group_list=query_sku_group(crawl_id)
    for sku_group in sku_group_list:
        get_comment_count.delay(sku_group,crawl_id)
        
    
    
    
    
    
    
    
    