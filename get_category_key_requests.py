# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 21:37:59 2017
抓取关键品类的品牌
@author: Administrator
"""

import requests
import json
import pymysql
import datetime

#下载网页，若失败返回空文本
def load(category_level3_id):
    url = 'https://list.jd.com/list.html'
    params = {'cat' : category_level3_id,
              'trans' : 1,
              'md' : 1,
              'my' : 'list_brand'}
    try:
        response = requests.get(url, params=params)
        txt = response.text
    except:
        print('get_category-error-load:%s' % category_level3_id)
        txt = ''
    return txt
    
#解析网页，返回品牌列表，若失败返回空
def parse(txt, category_level3_id):
    brands_list = []
    try:
        txt_dict = json.loads(txt)
        catalog_level1_name = txt_dict['summary']['cate_infos']['cat1_name']
        catalog_level2_name = txt_dict['summary']['cate_infos']['cat2_name']
        catalog_level3_name = txt_dict['summary']['cate_infos']['cat3_name']
        brands = txt_dict['brands']
        if brands is not None:
            for brand in brands:
                brand_id = str(brand['id'])
                brand_name = brand['name']
                brand_record = [brand_id, brand_name, category_level3_id,\
                                catalog_level3_name, catalog_level2_name,\
                                catalog_level1_name]
                brands_list.append(brand_record)
        else:
            brands_list = []               
    except:
        brands_list = []
        print('get_category-error-parse:%s' % category_level3_id)
    return brands_list

#存入mysql
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1',user='root',password='1111',\
                           db='customer',charset='utf8', port=3306)
    cur = conn.cursor()
    sql = 'insert into category_key_jd(crawl_id,brand_id, brand_name,category_level3_id,\
    category_level3_name,category_level2_name,category_level1_name,crawl_date,crawl_time)\
    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql, record)
        conn.commit()
    except:
        print('get_category-error:不能存入数据库%s' % record)
        pass
    cur.close()
    conn.close()


if __name__=='__main__':
    crawl_id = input('请输入抓取编号（形如201608）：')
    category_level3_id = input('输入三级类别编码：')
    crawl_date = datetime.date.today()
    now = datetime.datetime.now()
    crawl_time = now.strftime('%H:%M:%S')
    txt = load(category_level3_id)
    if txt != '':
        brands_list = parse(txt, category_level3_id)
        if len(brands_list) > 0:
            for brand in brands_list:
                record = [crawl_id] + brand + [crawl_date, crawl_time]
                input_mysql(record)
