# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 15:02:17 2016
get sku price from jd by sku_a,sku_b,sku_c(手机APP)
1.price
2.supplier
3.time
sn:136368730
jd:2024551
url:http://item.m.jd.com/product/2024551.html
@author: 14020199
"""
import sku_b
import requests
import bs4
import datetime
import pymysql

def get_price(sku):
    price_list=[]
    url_sku=url_base+str(sku)+'.html'
    try:
        response_sku=requests.get(url_sku,proxies=proxies).text
        soup_sku=bs4.BeautifulSoup(response_sku,'html.parser')
        price=soup_sku.find('input',id='jdPrice').get('value')
        soup_new=soup_sku.select('.provide-srv')
        vendor=soup_new[1].p.string
        crawldate=datetime.date.today()
        now=datetime.datetime.now()
        crawltime=now.strftime('%H:%M')
        price_list=[sku,price,vendor,crawldate,crawltime]
        return price_list
    except:
        return 0

if __name__=='__main__':
    sku_b=sku_b.get_sku()
    url_base='http://item.m.jd.com/product/'
    proxies={'http':'http://10.19.110.31:8080'}
    conn=pymysql.connect(host='127.0.0.1',user='root',passwd='1111',db='customer',charset='utf8')
    cur=conn.cursor()
    sql='insert into price_jd values(%s,%s,%s,%s,%s)'
    sku_b_error=[]
    for i in sku_b:
        price=get_price(i)
        if price:
            try:
                cur.execute(sql,price)
                conn.commit()
            except:
                sku_b_error.append(i)
                continue
        else:
            continue
    cur.close()
    conn.close()
    
        