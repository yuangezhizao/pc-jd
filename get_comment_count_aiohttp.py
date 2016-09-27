# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 09:24:31 2016

http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=3243686

@author: thinkpad
"""
import asyncio
import aiohttp
import aiomysql
import pandas as pd
import datetime
import queue

'''
def get_sku_group(num=500):
    global crawl_id
    sku_group_queue=queue.Queue()
    conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',
                         db='customer')
    sql='select distinct sku_jd.sku_group from sku_jd where sku_jd.sku_group \
    not in (select comment_count_jd.sku_group from comment_count_jd where \
    comment_count_jd.crawl_id=%s) limit %d'%(crawl_id,num)
    sku_group_df=pd.read_sql(sql,conn)
    for sku_group in sku_group_df['sku_group']:
        sku_group_queue.put(sku_group)
    conn.close()
    return sku_group_queue
'''

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
            conn=await aiomysql.connect(host='127.0.0.1',user='root',password='1111',
                         db='customer')
            cur=await conn.cursor()
            sql='insert into comment_count_jd(crawl_id,sku_group,score1_count,\
            score2_count,score3_count,score4_count,score5_count,show_count,\
            comment_count,average_score,good_count,good_rate,good_rate_show,\
            good_rate_style,general_count,general_rate,general_rate_show,\
            general_rate_style,poor_count,poor_rate,poor_rate_show,poor_rate_style,\
            crawl_date,crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            await cur.execute(sql,count)
            await conn.commit()
            await cur.close()
            conn.close()
            
            
if __name__=='__main__':
    crawl_id=input('请输入爬取编号：')
    sku_group_queue=queue.Queue()
    sku_group_dt=pd.read_csv('C:/Users/Administrator/Documents/Temp/sku_group.csv',dtype=str)
    for sku_group in sku_group_dt['sku_group']:
        sku_group_queue.put(sku_group)
    while sku_group_queue.qsize()>0:
        loop=asyncio.get_event_loop()
        tasks=[]
        for n in range(0,500):
            task=asyncio.ensure_future(get_count(sku_group_queue.get()))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))

