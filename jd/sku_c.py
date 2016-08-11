# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 21:26:29 2016
将jd商品按评论数量分为a,b,c三类
@author: 14020199
"""
import pandas as pd
import pymysql
import gc

def get_sku():
    conn=pymysql.connect(host='127.0.0.1',user='root',passwd='1111',db='customer',charset='utf8')
    sql='select sku,comments from jd where comments>0'
    sku=pd.read_sql(sql,conn)
    sku=sku.drop_duplicates('sku')
    sku.sort(columns='comments',ascending=False,inplace=True)
    sku['cum_comments']=sku['comments'].cumsum()
    sku['ratio']=sku['cum_comments']/sum(sku['comments'])
    #sku_a=sku['sku'][sku.ratio<=0.9]#35w
    #sku_b=sku['sku'][(sku.ratio>0.9)&(sku.ratio<=0.97)]#62w
    sku_c=sku['sku'][sku.ratio>0.97]
    conn.close()
    del sku
    gc.collect()
    return sku_c
