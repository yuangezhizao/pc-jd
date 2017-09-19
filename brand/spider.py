# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 16:25:51 2017
品牌爬虫
@author: Administrator
"""

import get_brand
import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import config.store as store

category_level3_id = '9987,653,655'
crawl_id = input('输入抓取编号（20170905）：')
sql = 'insert into brand_jd(                                          \
                  crawl_id,                                           \
                  category_level3_id,                                 \
                  category_level3_name,                               \
                  category_level2_name,                               \
                  category_level1_name,                               \
                  brand_id,                                           \
                  brand_name,                                         \
                  crawl_time)                                         \
        values(%s,%s,%s,%s,%s,%s,%s,%s)'
txt = get_brand.load(category_level3_id)
if txt:
    records = []
    brands = get_brand.parse(txt)
    for brand in brands:
        record = [crawl_id, category_level3_id] + brand
        records.append(record)
    store.store(sql, records)
        