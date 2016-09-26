# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 21:35:13 2016
一、功能
根据京东商品类别（category_jd.category_level3_id），抓取全部的SKU，并存入数据库
[crawl_id,sku,sku_group,category_level3_id,crawl_date,crawl_time]

二、逻辑
1.三级类别页面：http://list.jd.com/list.html?cat=1315,1342,1348
2.获取三级类别页面的页数
3.构造每页的URL：http://list.jd.com/list.html?cat=1315,1342,1348&page=1
4.抓取每页URL中的sku
@author: thinkpad
"""
import requests
import bs4
import re
import pymysql
import datetime
import pandas as pd
import time
import random

def get_page_number(category_level3_id):                                     #抓取三级类别页面的页数
    url='http://list.jd.com/list.html?cat='+str(category_level3_id)
    response=requests.get(url).text
    soup=bs4.BeautifulSoup(response,'html.parser')
    span=soup.select('.p-skip')
    page_number=int(span[0].em.b.string)
    return page_number

def input_mysql(sku_list):
    conn=pymysql.connect(host='127.0.0.1',user='root',password='root',db='customer',charset='utf8')
    cur=conn.cursor()
    sql='insert into sku_jd(crawl_id,sku,sku_group,category_level3_id,\
    crawl_date,crawl_time) values(%s,%s,%s,%s,%s,%s)'
    cur.execute(sql,sku_list)
    conn.commit()
    cur.close()
    conn.close()

def get_sku(crawl_id,category_level3_id,page_number):                        #抓取每页中的sku
    for page in range(1,page_number+1):
        crawl_date=datetime.date.today()
        now=datetime.datetime.now()
        crawl_time=now.strftime('%H:%M:%S')
        url='http://list.jd.com/list.html?cat='+str(category_level3_id)+\
        '&page='+str(page)
        try:
            response=requests.get(url).text
            ware_list=re.findall('(?<=slaveWareList =).+(?=;)',response)     #抓取slaveWareList
            ware_dict=eval(ware_list[0])                                     #转换成字典
            for sku_group in ware_dict:
                sku_group_string=str(sku_group)
                sku_list=[crawl_id,sku_group_string,sku_group_string,\
                category_level3_id,crawl_date,crawl_time]
                input_mysql(sku_list)
                for sku_dict in ware_dict[sku_group]:
                    for sku in sku_dict:
                        sku_list=[crawl_id,sku,sku_group_string,\
                        category_level3_id,crawl_date,crawl_time]
                        input_mysql(sku_list)
            #time.sleep(3*random.random())
        except:
            print('category:%s,page:%s'%(category_level3_id,page))
            continue

def query_category():
    conn=pymysql.connect(host='127.0.0.1',user='root',password='root',db='customer',charset='utf8')
    #全部商品类别
    sql_all='select distinct category_level3_id from category_jd'                
    category_all=pd.read_sql(sql_all,conn)
    category_list_all=[]
    for c in category_all['category_level3_id']:
        category_list_all.append(c)
    #已爬取SKU的商品类别
    sql_crawled='select distinct category_level3_id from sku_jd'
    category_crawled=pd.read_sql(sql_crawled,conn)
    category_list_crawled=[]
    for c in category_crawled['category_level3_id']:
        category_list_crawled.append(c)
    #未爬取SKU的商品类别
    category_list=[c for c in category_list_all if c not in category_list_crawled]  
    #前一次爬取时，最后一个爬取的类别
    sql_last='select category_level3_id from sku_jd order by id desc limit 1'
    category_last=pd.read_sql(sql_last,conn)
    for c in category_last['category_level3_id']:
        category_list.append(c)
    return category_list
    
    

if __name__=='__main__':
    crawl_id=input('请输入抓取编号（如201609）：')
    category_list=query_category()
    if len(category_list)==0:
        print('Sku crawled over!')
    else:
        for category_level3_id in category_list:
            try:
                page_number=get_page_number(category_level3_id)
            except:
                print('category:%s'%category_level3_id)
                continue
            get_sku(crawl_id,category_level3_id,page_number)
            #time.sleep(3*random.random())

    
        
        
        
        
        
        
        
        
        
        
        
        

