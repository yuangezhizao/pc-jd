# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 21:38:16 2017
抓取指定SKU的评论并存入数据库
@author: Administrator
"""

import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import config.store as store
import config.db as db
import psycopg2
import comment.get_comment as get_comment

def crawl(category_level3_id, brand_id, sku_list):
    for sku in sku_list:
        crawled_list = comment_crawled(sku)
        page = 0
        while True:
            comments = get_comment.get_comment(sku, page)
            if len(comments):
                sql = 'insert into comment_jd(category_level3_id, brand_id, sku, \
                       image_list_count, comment_id, content, creation_time,\
                       reference_time, reply_count, score, useful_vote_count, \
                       user_image_url, user_level_id, user_province, user_register_time, \
                       nickname, product_color, product_size, image_count,\
                       anonymous_flag, user_level_name, user_client_show, is_mobile, days,\
                       img_url, crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                comments_full = []
                for comment in comments:
                    if comment[1] in crawled_list:
                        pass
                    else:
                        comments_full.append([category_level3_id, brand_id, sku] + comment)
                store.store(sql, comments_full)
                page = page + 1
            else:
                break

#获取sku已抓取的评论id
def comment_crawled(sku):
    crawled_list = []
    conn = psycopg2.connect(host = db.host,
                            port = db.port,
                            user = db.user,
                            password = db.password,
                            database = db.database)
    cur = conn.cursor()
    sql = "select distinct comment_id          \
           from comment_jd                     \
           where sku='%s'" % sku
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        crawled_list.append(row[0])
    cur.close()
    conn.close()
    return crawled_list

if __name__ == '__main__':
    sku_list = ['5131309', '5131311', '5089239', '5089253',  '5131287', '5089235', '5131225', '5089237']
    crawl('9987,653,655', '14026', sku_list)
    
    
    
    
    