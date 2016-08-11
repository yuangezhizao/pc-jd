# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 20:41:17 2015
抓取京东商品
step1:获取品类url,如平板电视http://list.jd.com/list.html?cat=737,794,798
step2:由品类url获得sku编码
step3:由sku编码获得该商品的url
step4:抓取商品的sku,描述,价格,评论数量

@author: 14020199
"""

import requests
import bs4
import re
import pymysql
from time import ctime
import pickle
import queue
import threading
#step3:sku，描述，评论数
proxies={'http':'http://10.19.110.31:8080'}
headers1={'user-agent':'Mozilla/5.0 (Windows NT 6.1; rv:42.0) Gecko/20100101 Firefox/42.0'}
headers2={'user-agent':'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
conn=pymysql.connect(host='127.0.0.1',user='root',passwd='1111',db='customer',charset='utf8')
cur=conn.cursor()
url_queue=queue.Queue(0)

file=open('d:/url_rest.pkl','rb')
b=pickle.load(file)
file.close()
for u in b[24391:93695]:
    url_queue.put(u)

url_scanned=[]
url_error=[]
file_error=open('d:/url_error.pkl','wb')
def crawler(url_queue):
    while url_queue.qsize()>0:
        url=url_queue.get()
        url_scanned.append(url)
        try:
            if url_queue.qsize()%2==0:
                response_url=requests.get(url,proxies=proxies,headers=headers1).text
            else:
                response_url=requests.get(url,proxies=proxies,headers=headers2).text
            soup_url=bs4.BeautifulSoup(response_url,'html.parser')
            for s in soup_url.find_all('a',target='_blank'):
                try:
                    if s.get('href')[-4:]=='list':
                        sku=re.findall('\d+',s.get('href'))
                        comments=s.string
                        crawldate=ctime()
                        jd=[sku,comments,crawldate,url]
                        sql='insert into jd(sku,comments,crawldate,url) values(%s,%s,%s,%s)'
                        cur.execute(sql,jd)
                        conn.commit()
                    else:
                        continue
                except:
                    continue
        except:
            url_error.append(url)
            pickle.dump(url_error,file_error,True)
            continue
    return

crawler(url_queue)
'''threads=[]
t1=threading.Thread(target=crawler,args=(url_queue,))
threads.append(t1)
t2=threading.Thread(target=crawler,args=(url_queue,))
threads.append(t2)
for t in threads:
    t.setDaemon(True)
    t.start()
t.join()'''
