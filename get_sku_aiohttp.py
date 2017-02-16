# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 21:35:13 2016
一、功能
根据京东商品类别（category_level3_id）和品牌(brand_id)，抓取全部的SKU

二、逻辑
1.获取待抓取的商品类别和品牌
（1）从category_jd获取所有的商品类别-品牌
（2）从sku_jd获取已抓取的商品类别-品牌
（3）从（1）和（2）得到待抓取的商品类别-品牌
2.抓取1中商品类别-品牌的所有SKU
（1）https://list.jd.com/list.html?cat=商品类别&ev=exbrand_品牌&page=页码
@author: thinkpad
"""
import asyncio
import aiohttp
import aiomysql
import requests
import bs4
import re
import pymysql
import datetime
import pandas as pd

#获取待抓取的商品类别和品牌
def query_category(crawl_id_category, crawl_id_sku):
    conn = pymysql.connect(host='127.0.0.1',user='root',password='1111',db='customer',charset='utf8')
    #全部商品类别
    sql_all = 'select distinct concat(category_level3_id, "-", brand_id) as category\
               from category_jd where crawl_id=%s'%crawl_id_category             
    category_all = pd.read_sql(sql_all, conn)
    category_list_all = []
    for c in category_all['category']:
        category_list_all.append(c)
    #已爬取SKU的商品类别
    sql_crawled = 'select distinct concat(category_level3_id, "-", brand_id) as category\
                   from sku_jd_2 where crawl_id=%s'%crawl_id_sku
    category_crawled = pd.read_sql(sql_crawled, conn)
    conn.close()
    category_list_crawled = []
    for c in category_crawled['category']:
        category_list_crawled.append(c)
    #未爬取SKU的商品类别
    category_list = [c for c in category_list_all if c not in category_list_crawled]  
    return category_list

#获取商品类别-品牌的页数
def get_page_number(category_level3_id, brand_id):
    url='https://list.jd.com/list.html?cat=%s&ev=exbrand_%s&page=1'%(category_level3_id, brand_id)
    response=requests.get(url).text
    soup=bs4.BeautifulSoup(response,'html.parser')
    try:
        span=soup.select('.p-skip')
        page_number=int(span[0].em.b.string)
    except:
        page_number = 1
    return page_number

#抓取每页中的sku
def get_sku(crawl_id,category_level3_id,brand_id,page_number):               
    for page in range(1,page_number+1):
        crawl_date=datetime.date.today()
        now=datetime.datetime.now()
        crawl_time=now.strftime('%H:%M:%S')
        url='https://list.jd.com/list.html?cat=%s&ev=exbrand_%s&page=%s'%(category_level3_id,brand_id,page)
        try:
            response=requests.get(url).text
            ware_list=re.findall('(?<=slaveWareList =).+(?=;)',response)     #抓取slaveWareList
            ware_dict=eval(ware_list[0])                                     #转换成字典
            for sku_group in ware_dict:
                sku_group_string=str(sku_group)
                sku_list=[crawl_id,sku_group_string,sku_group_string,brand_id,\
                          category_level3_id,crawl_date,crawl_time]
                input_mysql(sku_list)
                for sku_dict in ware_dict[sku_group]:
                    for sku in sku_dict:
                        sku_list=[crawl_id,sku,sku_group_string,brand_id,\
                                  category_level3_id,crawl_date,crawl_time]
                        input_mysql(sku_list)
            #time.sleep(3*random.random())
        except:
            print('%s-%s第%s页失败'%(category_level3_id,brand_id,page))
            continue
#存入数据库
def input_mysql(sku_list):
    conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',db='customer',charset='utf8')
    cur=conn.cursor()
    sql='insert into sku_jd_2(crawl_id,sku,sku_group,brand_id,category_level3_id,\
    crawl_date,crawl_time) values(%s,%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql,sku_list)
        conn.commit()
    except:
        print('存入数据库失败%s'%sku_list)
        pass
    cur.close()
    conn.close()  

if __name__=='__main__':
    crawl_id=input('请输入抓取编号（如201609）：')
    category_list=query_category('201611','201611')
    if len(category_list)==0:
        print('Sku crawled over!')
    else:
        n = 0
        for category in category_list:
            category_level3_id = category.split('-')[0]
            brand_id = category.split('-')[1]
            page_number=get_page_number(category_level3_id, brand_id)
            get_sku(crawl_id,category_level3_id,brand_id,page_number)
            n = n+1
            print('品类%s品牌%s已完成(%s/%s)'%(category_level3_id, brand_id, n, len(category_list)))

    
        
        
        
        
        
        
        
        
        
        
        
        

