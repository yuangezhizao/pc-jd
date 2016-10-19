# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 13:28:21 2016 @南京图书馆
一、功能
抓取京东商品类别，并存入数据库
[三级类别编码，三级类别名称，二级类别名称，一级类别名称]
[737,738,751，电风扇，生活电器，家用电器]
二、逻辑
1.首页商品目录（storeys--storey--catalogs--catalog）
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
2.商品目录转换成商品类别【catalog-->category】
（1）如果二级目录编码是“737,794,870”形式，那么三级类别编码=二级目录编码，三级类别名称=二级目录名称，二级类别名称=二级目录名称，一级类别名称=一级目录名称
（2）否则，如果三级目录编码是“737,794,870”形式，那么三级类别编码=三级目录编码，三级类别名称=三级目录名称，二级类别名称=二级目录名称，一级类别名称=一级目录名称
（3）否则，如果三级目录编码是“6196-6197”形式，那么向下爬http://channel.jd.com/6196-6197.html获取三级类别编码和名称，二级类别名称=三级目录名称，一级类别名称=一级目录名称
3.商品目录URL：http://dc.3.cn/category/get?callback=getCategoryCallback
（1）"s"：下一级
（2）"n"：名称，含名字、编码和URL等
@author: thinkpad
"""

import requests
import json
import re
import bs4
import pymysql
import datetime
import time

#存入mysql
def input_mysql(category):
    conn=pymysql.connect(host='127.0.0.1',user='root',password='1111',db='customer',charset='utf8')
    cur=conn.cursor()
    sql='insert into category_jd(crawl_id,category_level3_id,\
    category_level3_name,category_level2_name,category_level1_name,crawl_date)\
    values(%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql,category)
        conn.commit()
    except:
        pass
    cur.close()
    conn.close()

#条件3
def get_category_case3(catalog_level3_id2,catalog_level3_name,\
catalog_level1_name,crawl_id,crawl_date): #抓取'123-123'形式的三级目录的类别，条件3
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
                    category_level3_name=s.string#.split()[0]                 #去掉名称中的空客
                    category_level2_name=catalog_level3_name
                    category_level1_name=catalog_level1_name
                    category=[crawl_id,category_level3_id,category_level3_name,\
                    category_level2_name,category_level1_name,crawl_date]
                    input_mysql(category)
                else:
                    continue

#主函数         
def get_category():
    crawl_id=input('请输入抓取编号（形如201608）：')
    crawl_date=datetime.date.today()
    storeys_url='http://dc.3.cn/category/get?callback=getCategoryCallback'      #京东首页目录楼层地址
    response=requests.get(storeys_url)                                         
    response.encoding='gb2312'
    response_text=response.text
    storeys_json=json.loads(response_text[20:-1])
    storeys=storeys_json['data']                                             #storeys目录楼
    for i in range(0,len(storeys)):                                          #遍历目录楼
        storey=storeys[i]                                                    #storey第i层目录楼
        catalogs_level1=storey['s']                                          #catalogs_level1第i层的所有一级目录catalogs_level1
        catalog_level1_name = ''
        for j in range(0, len(catalogs_level1)):
            catalog_level1_name = catalog_level1_name+catalogs_level1[j]['n'].split('|')[1]
        for j in range(0,len(catalogs_level1)):                                 #遍历一级目录
            catalog_level1=catalogs_level1[j]                                #catalog_level1第i层的第j个一级目录
            #catalog_level1_name=catalog_level1['n'].split('|')[1]               #第j个一级目录名称
            catalogs_level2=catalog_level1['s']                              #catalogs_level2第j个一级目录的所有二级目录
            for k in range(0,len(catalogs_level2)):                             #遍历二级目录
                catalog_level2=catalogs_level2[k]                            #catalog_level2第j个一级目录的第k个二级目录
                catalog_level2_n=catalog_level2['n']                            #二级目录的名称字符串
                catalog_level2_id=re.findall('\d+[,-]\d+[,-]\d+',catalog_level2_n) #catalog_level2_code二级目录编码
                catalog_level2_name=catalog_level2_n.split('|')[1]           #catalog_level2_name二级目录名称
                if len(catalog_level2_id)>0:                                 #条件1
                    category_level3_id=catalog_level2_id[0].replace('-',',') #category_level3_id三级类别编码
                    category_level3_name=catalog_level2_name                 #category_level3_name三级类别名称
                    category_level2_name=catalog_level2_name                 #category_level2_name二级类别名称
                    category_level1_name=catalog_level1_name                 #category_level1_name一级类别名称
                    category=[crawl_id,category_level3_id,category_level3_name,\
                    category_level2_name,category_level1_name,crawl_date]
                    input_mysql(category)
                else:
                    catalogs_level3=catalog_level2['s']                      #catalogs_level3二级目录包含的所有三级目录
                    for l in range(0,len(catalogs_level3)):                     #遍历三级目录
                        catalog_level3=catalogs_level3[l]
                        catalog_level3_n=catalog_level3['n']                    #三级目录的名称字符串
                        catalog_level3_id1=re.findall('\d+[,-]\d+[,-]\d+',\
                        catalog_level3_n)                                    #catalog_level3_id1三级目录编码1
                        catalog_level3_id2=re.findall('\d+-\d+',\
                        catalog_level3_n)                                    #catalog_level3_id2三级目录编码2
                        catalog_level3_name=catalog_level3_n.split('|')[1]
                        if len(catalog_level3_id1)>0:                        #条件2
                            category_level3_id=catalog_level3_id1[0].replace('-',',')
                            category_level3_name=catalog_level3_name
                            category_level2_name=catalog_level2_name
                            category_level1_name=catalog_level1_name
                            category=[crawl_id,category_level3_id,\
                            category_level3_name,category_level2_name,\
                            category_level1_name,crawl_date]
                            input_mysql(category)
                        elif len(catalog_level3_id2)>0:                      #条件3
                            get_category_case3(catalog_level3_id2,\
                            catalog_level3_name,catalog_level1_name,crawl_id,\
                            crawl_date)

if __name__=='__main__':
    start_time=time.time()
    get_category()
    end_time=time.time()
    print('爬取时间是%s秒'%(end_time-start_time))