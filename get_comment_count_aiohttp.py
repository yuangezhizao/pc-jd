# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 09:24:31 2016

http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=3243686

@author: thinkpad
"""
import asyncio
import aiohttp
import pymysql
import pandas as pd
import time
import datetime

def get_sku_group(num=500):
    global crawl_id
    sku_group_list=[]
    conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',
                         db='customer')
    sql='select distinct sku_jd.sku_group from sku_jd where sku_jd.sku_group \
    not in (select comment_count_jd.sku_group from comment_count_jd where \
    comment_count_jd.crawl_id=%s) limit %d'%(crawl_id,num)
    sku_group_df=pd.read_sql(sql,conn)
    for sku_group in sku_group_df['sku_group']:
        sku_group_list.append(sku_group)
    conn.close()
    return sku_group_list

async def get_count(sku_group):
    global crawl_id
    url_base='http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds='
    url=url_base+str(sku_group)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            count_text=await response.read()
            count_dict=eval(count_text)
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
            conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',
                         db='customer')
            cur=conn.cursor()
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
            
'''
def parse(text):
    global crawl_id
    count_dict=eval(text)
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
    #crawl_date=datetime.date.today()
    #now=datetime.datetime.now()
    #crawl_time=now.strftime('%H:%M:%S')
    count=[score1_count,score2_count,score3_count,\
           score4_count,score5_count,show_count,comment_count,average_score,
           good_count,good_rate,good_rate_show,good_rate_style,
           general_count,general_rate,general_rate_show,general_rate_style,
           poor_count,poor_rate,poor_rate_show,poor_rate_style]
    return count
'''
if __name__=='__main__':
    crawl_id=input('请输入爬取编号：')
    start=time.time()
    loop=asyncio.get_event_loop()
    tasks=[]
    sku_group_list=get_sku_group(num=500)
    for sku_group in sku_group_list:
        task=asyncio.ensure_future(get_count(sku_group))
        tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
    end=time.time()
    print('interval:%s'%(end-start))

