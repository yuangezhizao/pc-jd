# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 08:00:02 2016

@author: Administrator
"""

import requests
import pymysql
import datetime
import pandas as pd

def get_count(crawl_id,sku_group):
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
        sql='insert into comment_count_jd_copy(crawl_id,sku_group,score1_count,\
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

if __name__=='__main__':
    crawl_id=input('请输入爬取编号：')
    sku_group_dt=pd.read_csv('C:/Users/Administrator/Documents/Temp/sku_group.csv',dtype=str)
    for sku_group in sku_group_dt['sku_group']:
        get_count(crawl_id,sku_group)
