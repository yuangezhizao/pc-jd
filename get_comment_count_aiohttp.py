# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 09:24:31 2016

http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=3243686

@author: thinkpad
"""
import asyncio
import aiohttp
import pymysql
import aiomysql
import pandas as pd
import time

async def get_count(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text=await response.read()
            count=parse(text)
            print(count)

def make_url(num=10):
    url_list=[]
    url_base='http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds='
    conn=pymysql.connect(host='127.0.0.1',user='root',password='root',db='customer')
    sql='select sku from sku_jd limit %s'%num
    sku_list=pd.read_sql(sql,conn)
    conn.close()
    for sku in sku_list['sku']:
        url=url_base+str(sku)
        url_list.append(url)
    return url_list

def parse(text):
    text_dict=eval(text)
    score_1_count=text_dict['CommentsCount'][0]['Score1Count']
    score_2_count=text_dict['CommentsCount'][0]['Score2Count']
    score_3_count=text_dict['CommentsCount'][0]['Score3Count']
    score_4_count=text_dict['CommentsCount'][0]['Score4Count']
    score_5_count=text_dict['CommentsCount'][0]['Score5Count']
    count=[score_1_count,score_2_count,score_3_count,score_4_count,score_5_count]
    return count

if __name__=='__main__':
    start=time.time()
    loop=asyncio.get_event_loop()
    tasks=[]
    n=10
    while n>0:
        url_list=make_url(num=1000)
        for url in url_list:
            task=asyncio.ensure_future(get_count(url))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        end=time.time()
        print('interval:%s'%(end-start))
        n=n-1


