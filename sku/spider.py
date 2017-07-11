# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 21:37:31 2017
爬取指定三级编码的所有SKU
@author: Administrator
"""

import get_sku
import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import config.db as db
import psycopg2
import pandas as pd
import datetime
import logging

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s:%(message)s')

#获取待抓取的品牌
def get_brand(category_level3_id):
    conn = psycopg2.connect(host = db.host, 
                            port = db.port, 
                            database = db.database,
                            user = db.user,
                            password = db.password)
    sql = 'select distinct brand_id                 \
           from brand_jd                            \
           where crawl_id=(select crawl_id from brand_jd order by id desc limit 1)'
    brand = pd.read_sql(sql, conn)
    conn.close()
    return brand['brand_id']

#获取sku主函数，并存入数据库
def crawl(crawl_id, category_level3_id, brand_id):
    conn = psycopg2.connect(host = db.host, 
                            port = db.port, 
                            database = db.database,
                            user = db.user,
                            password = db.password)
    cur = conn.cursor()
    sql = 'insert into sku_jd(                        \
                       crawl_id,                      \
                       category_level3_id,            \
                       brand_id,                      \
                       sku_group,                     \
                       sku,                           \
                       sku_name,                      \
                       vender_id,                     \
                       shop_id,                       \
                       sku_specs,                     \
                       crawl_time)                    \
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    #获取页数
    pages = get_sku.get_pages(category_level3_id, brand_id)
    if pages:
        for page in range(1, pages+1):
            logging.info('%s-%s第%s页' % (category_level3_id, brand_id, page))
            #获取第page页的sku_group
            sku_group_list = get_sku.get_sku_group(category_level3_id, brand_id, page)
            if len(sku_group_list) > 0:
                for sku_group in sku_group_list:
                    #获取sku_group对应的sku
                    sku_list = get_sku.get_sku_from_sku_group(sku_group)
                    if len(sku_list) > 0:
                        for sku in sku_list:
                            #获取sku参数
                            params = get_sku.get_sku_params(sku)
                            params.insert(0, sku)
                            params.insert(0, sku_group)
                            params.insert(0, brand_id)
                            params.insert(0, category_level3_id)
                            params.insert(0, crawl_id)
                            now = datetime.datetime.now()
                            crawl_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            params.append(crawl_time)
                            try:
                                cur.execute(sql, params)
                                conn.commit()
                            except:
                                print('error: crawl: 存入数据库%s' % sku)

if __name__ == '__main__':
    crawl_id = '20170711'
    category_level3_id = '9987,653,655'
    brand_id_list = get_brand(category_level3_id)
    for brand_id in brand_id_list:
        crawl(crawl_id, category_level3_id, brand_id)

