# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 13:28:21 2016 @南京图书馆
一、功能
抓取京东商品类别和品牌

二、逻辑
1.抓取三级类别编码（http://dc.3.cn/category/get?callback=getCategoryCallback）
（1）首页商品目录（storeys--storey--catalogs--catalog）
    全部商品分类：【catalog 目录】
    1.家用电器 【catalog_level1 一级目录】
      1.1 电视 【catalog_level2 二级目录】
        1.1.1 合资品牌 【catalog_level3 三级目录】
        1.1.2 国产品牌
        1.1.3 互联网品牌
      1.2 空调
      ...
      1.9 家庭影音
    2.手机、数码、京东通信
    3.电脑、办公
    ...
    15.理财、众筹、白条、保险 【共15层】
（2）case1: 如果二级目录编码是“737,794,870”形式，进入2
（3）case2: 否则，如果三级目录编码是“737,794,870”形式，进入2
（4）case3: 否则，如果三级目录编码是“6196-6197”形式，向下爬http://channel.jd.com/6196-6197.html获取三级类别编码，进入2
2.抓取1中三级类别编码的品牌和各级类别的名称（https://list.jd.com/list.html?cat=三级类别编码&trans=1&md=1&my=list_brand）
（1）解析['brands']中的['id']和['name']
（2）解析['summary']['cate_infos']中的['cat1_name']、['cat2_name']和['cat3_name']

三、禁爬规则
无

四、更新记录
1.更改数据来源
之前：
（1）http://dc.3.cn/category/get?callback=getCategoryCallback		
（2）http://channel.jd.com/6196-6197.html
现在：			
（1）http://dc.3.cn/category/get?callback=getCategoryCallback
（2）http://channel.jd.com/6196-6197.html
（3）https://list.jd.com/list.html?cat=三级类别编码&trans=1&md=1&my=list_brand
"""

import requests
import json
import re
import bs4
import pymysql
import datetime
import time
import random

#抓取category_level3_id        
def get_category_level3_list():
    storeys_url='http://dc.3.cn/category/get?callback=getCategoryCallback'      #京东首页目录楼层地址
    response=requests.get(storeys_url)                                         
    response.encoding='gb2312'
    response_text=response.text
    storeys_json=json.loads(response_text[20:-1])
    storeys=storeys_json['data']                                             #storeys目录楼
    for i in range(0,len(storeys)):                                          #遍历目录楼
        storey=storeys[i]                                                    #storey第i层目录楼
        catalogs_level1=storey['s']                                          #catalogs_level1第i层的所有一级目录catalogs_level1
        for j in range(0,len(catalogs_level1)):                                 #遍历一级目录
            catalog_level1=catalogs_level1[j]                                #catalog_level1第i层的第j个一级目录
            catalogs_level2=catalog_level1['s']                              #catalogs_level2第j个一级目录的所有二级目录
            for k in range(0,len(catalogs_level2)):                             #遍历二级目录
                catalog_level2=catalogs_level2[k]                            #catalog_level2第j个一级目录的第k个二级目录
                catalog_level2_n=catalog_level2['n']                            #二级目录的名称字符串
                catalog_level2_id=re.findall('\d+[,-]\d+[,-]\d+',catalog_level2_n) #catalog_level2_code二级目录编码
                if len(catalog_level2_id)>0:                                 #条件1
                    category_level3_id=catalog_level2_id[0].replace('-',',') #category_level3_id三级类别编码
                    if category_level3_id not in category_level3_list:
                        category_level3_list.append(category_level3_id)
                else:
                    catalogs_level3=catalog_level2['s']                      #catalogs_level3二级目录包含的所有三级目录
                    for l in range(0,len(catalogs_level3)):                     #遍历三级目录
                        catalog_level3=catalogs_level3[l]
                        catalog_level3_n=catalog_level3['n']                    #三级目录的名称字符串
                        catalog_level3_id1=re.findall('\d+[,-]\d+[,-]\d+',\
                        catalog_level3_n)                                    #catalog_level3_id1三级目录编码1
                        catalog_level3_id2=re.findall('\d+-\d+',\
                        catalog_level3_n)                                    #catalog_level3_id2三级目录编码2
                        if len(catalog_level3_id1)>0:                        #case2
                            category_level3_id=catalog_level3_id1[0].replace('-',',')
                            if category_level3_id not in category_level3_list:
                                category_level3_list.append(category_level3_id)
                        elif len(catalog_level3_id2)>0:                      #case3
                            get_category_case3(catalog_level3_id2)
    return category_level3_list

#抓取三级类别编码：case3
def get_category_case3(catalog_level3_id2): #抓取'123-123'形式的三级目录的类别，case3
    url='http://channel.jd.com/'+str(catalog_level3_id2[0])+'.html'
    response=requests.get(url)
    response.encoding='gb2312'
    soup=bs4.BeautifulSoup(response.text,'html.parser')
    for s in soup.find_all('a'):
        href=s.get('href')
        if href is None:
            id_list=[]
        else:
            id_list=re.findall('\d+[,-]\d+[,-]\d+',href)                         #'123-123-123'形式
        if len(id_list)>0:                                                   #匹配有结果
            for i in id_list:
                if len(i)>10:                                                #长度大于10，排除非类别编码的查询结果
                    category_level3_id=i.replace('-',',')
                    if category_level3_id not in category_level3_list:
                        category_level3_list.append(category_level3_id)
                else:
                    continue

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
    sql = 'insert into category_jd(crawl_id,brand_id, brand_name,category_level3_id,\
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
    global category_level3_list
    category_level3_list = []
    category_level3_list = get_category_level3_list()
    n = 0
    for category_level3_id in category_level3_list:
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
        n = n+1
        time.sleep(random.randint(10,60))
        print('get_category:已完成%s/%s三级商品类别'%(n, len(category_level3_list)))
    
    