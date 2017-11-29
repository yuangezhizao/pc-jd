# -*- coding: utf-8 -*-
"""
爬虫：抓sku_group评论数量
1.获取抓取任务
2.抓取每个sku的评论数量，并比较得到sku_group的评论数量
3.存入数据库
"""

import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import config.db as db
import comment_count.get_task as get_task
import comment_count.get_comment_count as count
import logging
import datetime
import psycopg2


#日志
logger = logging.getLogger('spider01')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('C:/Users/Administrator/Documents/GitHub/pc-jd/comment/logger.txt')
pattern = logging.Formatter('%(asctime)s-%(filename)s[line: %(lineno)d]-%(funcName)s-%(levelname)s-%(message)s')
handler.setFormatter(pattern)
logger.addHandler(handler)

#爬取函数
def crawl(category_level3_id, crawl_id):
    conn = psycopg2.connect(host = db.host, 
                            port = db.port, 
                            database = db.database,
                            user = db.user,
                            password = db.password)
    cur = conn.cursor()
    sql = 'insert into comment_count_jd(              \
                       crawl_id,                      \
                       category_level3_id,            \
                       brand_id,                      \
                       sku_group,                     \
                       score1_count,                  \
                       score2_count,                  \
                       score3_count,                  \
                       score4_count,                  \
                       score5_count,                  \
                       comment_count,                 \
                       crawl_time)                    \
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'    
    #待爬取任务
    task = get_task.get_task(category_level3_id, crawl_id)
    for category_level3_id in task:
        for brand_id in task[category_level3_id]:
            for sku_group in task[category_level3_id][brand_id]:
                sku_list = task[category_level3_id][brand_id][sku_group]
                comment_count = 0
                comments = []
                for sku in sku_list:
                    i, j = count.get_comment_count(sku)
                    if i >= comment_count:
                        comment_count = i
                        comments = j
                now = datetime.datetime.now()
                crawl_time = now.strftime('%Y-%m-%d %H:%M:%S')
                record = [crawl_id, category_level3_id, brand_id, sku_group] + comments + [crawl_time]
                try:
                    cur.execute(sql, record)
                    conn.commit()
                    logger.info('%s-品牌%s-%s抓取成功' % (category_level3_id, brand_id, sku_group))
                except:
                    logger.error('不能存入数据库%s' % sku_group)

if __name__ == '__main__':
    category_level3_id = '9987,653,655'
    crawl_id = '20171129'
    crawl(category_level3_id, crawl_id)
        


