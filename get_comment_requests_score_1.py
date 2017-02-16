# -*- coding: utf-8 -*-
"""
2016-12-23
1.功能
抓取1分差评的内容（未设置crawl_id）
2.逻辑
（1）从crawl_order获取待抓取的三级类别category_level3_ids
（2）从comment_count获取待抓取的sku_group(comment_count>0)
（3）下载sku_group的评论内容
https://club.jd.com/comment/ \
productPageComments.action? \ #该商品组所有颜色、尺寸SKU的评论 skuProductPageComments：具体sku的评论
callback=fetchJSON_comment98vv116& \
productId=1231058806& \ #sku
score=0& \ # 1:差评 2：中评 3：好评 0：所有
sortType=6& \ # 6:时间排序 5：推荐排序
page=0& \ #页码
pageSize=10& \ #每页10条评论
isShadowSku=0

备用url: 
http://club.jd.com/productpage/p-255742-s-3-t-3-p-0.html?callback=fetchJSON_comment98vv17736
p:sku
s:score 1差评 2中评 3 好评
p:页码
（4）解析（3）中的内容
（5）判断（4）中的comment_id是否大于已抓取的最大的comment_id
（6）若（5）中是，则存入数据库
（7）更新规则：增量更新
两种方法：
a.新评论id > 旧评论id， 更新至旧评论中最大的id为止
b.新增的评论页数=当前评论页数-上次的评论页数，此种方法会有遗漏
3.禁爬规则
页数300左右时会没有响应
4.速度

"""
import requests
import json
import pymysql
import datetime
import pandas as pd
import time
import random

#获取爬取顺序，返回category_level3_id和数量
def get_category():
    category_level3_ids = []
    category = pd.read_csv('C:/Users/Administrator/Documents/GitHub/pc-jd/crawl_order.csv', 
                           encoding='gbk')
    category.sort_values(by='category_level3_order', inplace=True)
    for i in category['category_level3_id']:
        category_level3_ids.append(i.split('"')[1])
    n = len(category_level3_ids)
    return category_level3_ids, n

#获取comment_jd_score_1最新的已爬取的category_level3_id
def get_latest_crawled_category():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111',
                           db='customer', charset='utf8')
    sql = 'select category_level3_id from comment_jd_score_1 order by id desc limit 1'
    result = pd.read_sql(sql, conn)
    for i in result['category_level3_id']:
        latest_crawled_category = i
    conn.close()
    return latest_crawled_category

#获取待抓取的品牌-sku
def get_brand_sku(category_level3_id, is_add): #is_add是否增量抓取，1是，0否
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111',
                           db='customer', charset='utf8')
    #comment_count_jd所有的品牌-sku
    sku_all = []
    sql_all = 'select concat(brand_id, "-", sku_group) as sku\
               from comment_count_jd where crawl_id=(select crawl_id from comment_count_jd\
               order by id desc limit 1) and category_level3_id="%s" and comment_count > 0'\
               % category_level3_id #根据最新的crawl_id
    records_all = pd.read_sql(sql_all, conn)
    records_all = records_all.drop_duplicates('sku')
    for i in records_all['sku']:
        sku_all.append(i)
    #comment_jd_score_1已爬取的品牌-sku
    if not is_add:
        sku_crawled = []
        sql_crawled = 'select concat(brand_id, "-", sku_group) as sku\
                       from comment_jd_score_1 where category_level3_id="%s"'\
                       % category_level3_id
        records_crawled = pd.read_sql(sql_crawled, conn)
        records_crawled = records_crawled.drop_duplicates('sku')
        for i in records_crawled['sku']:
            sku_crawled.append(i)
        #未爬取的sku
        sku_task = [i for i in sku_all if i not in sku_crawled]
        sku_task.sort()
        n = len(sku_task)
    conn.close()
    return sku_task, n

#获取sku_group评论的页数，若失败，返回0
def get_pages(sku_group):
    url = 'https://club.jd.com/comment/productPageComments.action'
    params = {'callback':'fetchJSON_comment98vv116',
              'productId':sku_group,
              'score':1,
              'sortType':6,
              'page':0,
              'pageSize':10,
              'isShadowSku':0}
    try:
        txt = requests.get(url, params=params).text
        comment_dict = json.loads(txt[25:-2]) #截取长度和fetchJSON_comment98vv116有关
        pages = comment_dict['maxPage']
    except:
        print('get_comment_jd_score_1-error: get_pages: %s' % sku_group)
        pages = 0
    return pages

#下载sku_group的第page页评论文本，若失败返回空值
def load(sku_group, page):
    url = 'https://club.jd.com/comment/productPageComments.action'
    params = {'callback':'fetchJSON_comment98vv116',
              'productId':sku_group,
              'score':1,
              'sortType':6,
              'page':page,
              'pageSize':10,
              'isShadowSku':0}
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate, br',
               'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection':'keep-alive',
               'Cookie':'__jda=122270672.852353802.1474856712.1485220812.1485259508.160;\
                         unpl=V2_ZzNtbUUAQkF3WxZRLBFYUmJUFAhKAhZAcghAVnIRWVBjVhVUclRCFXMUR1RnGlkUZAIZXEVcQhBFCHZXeBhYBmYBG1hyZ3MWdThOZHIdXwdjARtcQWdzEkU4OgowQQFYNwATXUdnQBZ0DEZdeRpaNWYzEFVLX0oUdg5GZDB3XUhuBxFfRlVKFHY4R2R4;\
                         __jdv=122270672|offlintab.firefoxchina.cn|t_220520384_|tuiguang|6f0e3ba4f95f4f7d9ddd6173894d5d68|1485259508505;\
                         __jdu=852353802; ipLoc-djd=12-904-3379-0; ipLocation=%u6C5F%u82CF; areaId=12; cn=1;\
                         TrackID=1xERLbwIsJ4vTcdDWgOt2SFQqRrEj1Nqfvz5rtXc3_ln4C2LGW_qJ-DuOBavxz5ZsGAbKgvPRB_AJM1VMRm3xF-20QzKQTm3zsaQa2n_HLj8;\
                         pinId=eEjGiU8n5xTiJ9euZLy0oQ; pin=zhuangliaos; _tp=L5%2BAO9cJiDmWiXuD6wLNCw%3D%3D; _pst=zhuangliaos;\
                         mt_xid=V2_52007VwoWUV9cUFMeSikMUm8AFlZbXE4NF0hKQABlBhVOVFtSUgMeGg9QYQFCBVhZVw0vShhcA3sCEk5eXUNZHkIYVQ5nCiJQbVhiWh5NEVsBZQcTYlhe',
               'Host':	'club.jd.com',
               'Upgrade-Insecure-Requests':'1',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    try:
        response = requests.get(url, params=params, headers=headers)
        txt = response.text
    except:
        print('get_comment_jd_score_1-error: load: %s第%s页下载失败' % (sku_group, page))
        txt = ''
    return txt

#解析下载的内容
def parse(txt, sku_group):
    crawl_date = datetime.date.today()
    now = datetime.datetime.now()
    crawl_time = now.strftime('%H:%M:%S')
    comments_list = []
    try:
        comment_dict = json.loads(txt[25:-2])
        image_list_count = comment_dict['imageListCount']
        comments = comment_dict['comments']
        if len(comments) > 0:
            for i in range(0, len(comments)):
                comment = comments[i]
                comment_id = comment.get('id', 0)
                content = comment.get('content', '') 
                creation_time = comment.get('creationTime', '')
                reference_time = comment.get('referenceTime', '')
                reference_id = comment.get('referenceId', '')
                reference_name = comment.get('referenceName', '')
                reply_count = comment.get('replyCount', 0)
                score = comment.get('score', 0)
                useful_vote_count = comment.get('usefulVoteCount', 0)
                user_image_url = comment.get('userImageUrl', '') 
                user_level_id = comment.get('userLevelId', '')
                user_province = comment.get('userProvince', '')
                user_register_time = comment.get('userRegisterTime', '')
                nickname = comment.get('nickname', '') 
                product_color = comment.get('productColor', '')
                product_size = comment.get('productSize', '')
                image_count = comment.get('imageCount', 0)
                anonymous_flag = comment.get('anonymousFlag', 2)#2未知
                user_level_name = comment.get('userLevelName', '')
                user_client_show = comment.get('userClientShow', '')
                is_mobile = int(comment.get('isMobile', 2))
                days = comment.get('days', 0)
                comment_i = [image_list_count, comment_id, content, creation_time, 
                             reference_time, reference_id, reference_name, reply_count,
                             score, useful_vote_count, user_image_url, user_level_id,
                             user_province, user_register_time, nickname, product_color,
                             product_size, image_count, anonymous_flag, user_level_name,
                             user_client_show, is_mobile, days, crawl_date, crawl_time]
                comments_list.append(comment_i)
    except:
        print('get_comment_jd_score_1-error-parse:%s' % sku_group)
        comments_list = []
    return comments_list

#存入数据库
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', 
                           db='customer', charset='utf8') #设置编码格式
    cur = conn.cursor()
    sql = 'insert into comment_jd_score_1(category_level3_id, brand_id, sku_group, max_page,\
           page_index, image_list_count, comment_id, content, creation_time,\
           reference_time, reference_id, reference_name, reply_count, score,\
           useful_vote_count, user_image_url, user_level_id, user_province,\
           user_register_time, nickname, product_color, product_size, image_count,\
           anonymous_flag, user_level_name, user_client_show, is_mobile, days,\
           crawl_date, crawl_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s,\
           %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
           %s, %s, %s)'
    try:
        cur.execute(sql, record)
        conn.commit()
    except:
        print('get_comment_jd_score_1-error: input_mysql: 存入数据库失败%s' % record)
        pass
    cur.close()
    conn.close()
    
#主函数
def crawl():                                    
    category_level3_ids, n1 = get_category()
    if n1 > 0:
        latest_crawled_category = get_latest_crawled_category()                              
        for i in range(category_level3_ids.index(latest_crawled_category), n1): #避免从第一个遍历，只从最近爬取的遍历
            category_level3_id = category_level3_ids[i]
            brand_sku_list, n2 = get_brand_sku(category_level3_id, 0)
            if n2 > 0:
                for brand_sku in brand_sku_list:
                    brand_id = brand_sku.split('-')[0]
                    sku_group = brand_sku.split('-')[1]
                    pages = get_pages(sku_group)                        
                    if pages > 0:
                        print('get_comment_jd_score_1:品类进度%s/%s,%sSKU进度%s/%s' %\
                               ((category_level3_ids.index(category_level3_id)+1), n1,\
                               category_level3_id, (brand_sku_list.index(brand_sku)+1),\
                               n2))
                        for page in range(0, pages):
                            txt = load(sku_group, page)
                            if txt != '':
                                comments_list = parse(txt, sku_group)
                                if len(comments_list) > 0:
                                    for comment in comments_list: 
                                        record = [category_level3_id, brand_id,  
                                                  sku_group, pages, page] + comment
                                        input_mysql(record)
                                else:
                                    break #pages是所有评论的页数，不要遍历所有页数
                            if page > 0 and page % 200 == 0:
                                time.sleep(random.randint(300, 600))

if __name__ == '__main__':
    crawl()
