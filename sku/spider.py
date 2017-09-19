# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 21:37:31 2017
爬取指定三级编码的所有SKU
@author: Administrator
"""


import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import sku.get_sku as get_sku
import config.db as db
import psycopg2
import pandas as pd
import datetime
import logging


#日志
logger = logging.getLogger('spider')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('C:/Users/Administrator/Documents/GitHub/pc-jd/sku/logger.txt')
pattern = logging.Formatter('%(asctime)s-%(filename)s[line: %(lineno)d]-%(funcName)s-%(levelname)s-%(message)s')
handler.setFormatter(pattern)
logger.addHandler(handler)

#获取待抓取的品牌，支持中断重抓
def get_brand(category_level3_id, crawl_id):
    brand_list = []
    conn = psycopg2.connect(host = db.host, 
                            port = db.port, 
                            database = db.database,
                            user = db.user,
                            password = db.password)
    sql = "select distinct t1.brand_id                                        \
               from brand_jd t1                                               \
               where t1.crawl_id=(                                            \
                               select crawl_id                                \
                               from brand_jd                                  \
                               order by id desc                               \
                               limit 1)                                       \
               and t1.category_level3_id='%s'                                 \
               and t1.brand_id not in (                                       \
                               select distinct t2.brand_id                    \
                               from sku_jd t2                                 \
                               where t2.crawl_id='%s'                         \
                               and t2.brand_id not in (                       \
                                                        select brand_id       \
                                                        from sku_jd           \
                                                        order by id desc      \
                                                        limit 1))" % (category_level3_id, crawl_id)
    brand = pd.read_sql(sql, conn)
    conn.close()
    for b in brand['brand_id']:
        brand_list.append(b)
    return brand_list

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
                                logger.info('品类%s-品牌%s-%s/%s页-%s:%s抓取成功' % 
                                (category_level3_id, brand_id, page, pages, 
                                 sku_group, sku))
                            except:
                                logger.error('不能存入数据库%s' % sku)

if __name__ == '__main__':
    crawl_id = input('输入抓取编号（20170906）：')
    category_level3_id = '9987,653,655'
    brand_id_list = get_brand(category_level3_id, crawl_id)
    for brand_id in brand_id_list:
        logger.info('正在抓取%s-%s-%s/%s' % (category_level3_id, brand_id, 
                                         brand_id_list.index(brand_id), 
                                         len(brand_id_list)))
        crawl(crawl_id, category_level3_id, brand_id)

