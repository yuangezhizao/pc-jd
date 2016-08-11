# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 18:06:34 2015
抓取京东sku的名称
"""
import pymysql
import requests
import bs4
import re
import queue

def getSku():
    sku=queue.Queue(0)
    cur1=conn.cursor()
    sql_query='select distinct sku from jd'
    cur1.execute(sql_query)
    for i in cur1:
        sku.put(i[0])
    cur1.close()
    return sku
    
def getTitle(sku):
    proxies={'http':'http://10.19.110.31:8080'}
    url='http://item.jd.com/'+sku+'.html'
    response=requests.get(url,proxies=proxies).text
    soup=bs4.BeautifulSoup(response,'html.parser')
    title_string=soup.find('title').string #取标签内容
    title=re.findall('(?<=】).+(?=【)|^\w.+(?=【)',title_string) #零宽断言
    return title

if __name__=='__main__':
    conn=pymysql.connect(host='127.0.0.1',user='root',passwd='1111',db='customer',charset='utf8')
    cur2=conn.cursor()
    sku_error=[]
    sku_queue=getSku()
    while sku_queue.qsize()>0:
        sku=sku_queue.get()
        try:
            title=getTitle(sku)
            sku_list=[sku,title]
            sql_insert='insert into sku_title_jd(sku,title) values(%s,%s)'
            cur2.execute(sql_insert,sku_list)
            conn.commit()
        except:
            sku_error.append(sku)
            continue
    cur2.close()
    conn.close()
