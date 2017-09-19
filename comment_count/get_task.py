# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 13:08:16 2017
获取待抓取任务
1.根据输入的三级类别编码
2.获取所有的brand_id, sku_group, sku
3.获取已抓取的brand_id, sku_group, sku
4.计算待抓取的brand_id, sku_group, sku
@author: Administrator
"""

import psycopg2
import logging
import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import config.db as db

#日志
logger = logging.getLogger('get_task')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('C:/Users/Administrator/Documents/GitHub/pc-jd/comment/logger.txt')
pattern = logging.Formatter('%(asctime)s-%(filename)s[line: %(lineno)d]-%(funcName)s-%(levelname)s-%(message)s')
handler.setFormatter(pattern)
logger.addHandler(handler)

#crawl_id已抓取评论数量的最新crawl_id，返回字典
def get_task(category_level3_id, crawl_id):
    conn = psycopg2.connect(host = db.host,
                            port = db.port,
                            database = db.database,
                            user = db.user,
                            password = db.password)
    cursor = conn.cursor()
    sql = "select category_level3_id, brand_id, sku_group, sku      \
           from sku_jd                                              \
           where crawl_id=(select crawl_id from sku_jd              \
                           order by id desc limit 1)                \
           and category_level3_id='%s'                              \
           and sku_group not in (                                   \
               select sku_group                                     \
               from comment_count_jd                                \
               where crawl_id='%s'                                  \
               and category_level3_id='%s')" % (category_level3_id, crawl_id, category_level3_id)
    cursor.execute(sql)
    rows = cursor.fetchall()   
    task = {}
    #将rows转换为字典
    for row in range(0, len(rows)):
        cat = rows[row][0]
        brand = rows[row][1]
        group = rows[row][2]
        task.setdefault(cat, {})
        task[cat].setdefault(brand, {})
        task[cat][brand][group] = []
    for row in range(0, len(rows)):
        cat = rows[row][0]
        brand = rows[row][1]
        group = rows[row][2]
        sku = rows[row][3]
        task[cat][brand][group].append(sku) 
    conn.close()
    logger.info('抓取任务：%s个sku' % len(rows))
    return task
    
    
    
    
    
    
    
    
    