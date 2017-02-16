# -*- coding: utf-8 -*-
"""
2016-12-23
1.功能
根据三级类别和品牌抓取商品评论的内容
2.逻辑
（1）获取待抓取的三级类别和品牌
（2）获取待抓取的sku_group
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
（5）将（4）中的内容存入数据库
（6）更新规则：增量更新
两种方法：
a.新评论id > 旧评论id， 更新至旧评论中最大的id为止
b.新增的评论页数=当前评论页数-上次的评论页数，此种方法会有遗漏
3.禁爬规则
无
4.速度

"""
import requests
import json
import pymysql
import datetime
import pandas as pd

#获取待抓取的sku_group，返回data.frame
def get_sku_group(category_level3_id, brand_id):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer')
    sql = 'select sku_group from comment_count_jd \
           where category_level3_id="%s" and brand_id="%s" \
           and comment_count>0' % (category_level3_id, brand_id)
    sku_group_list = pd.read_sql(sql, conn)
    conn.close()
    if len(sku_group_list) == 0:
        print('message: %s - %s 没有待抓取任务' % (category_level3_id, brand_id))
    return sku_group_list

#获取sku_group评论的页数，若失败，返回0
def get_pages(sku_group):
    url = 'https://club.jd.com/comment/productPageComments.action'
    params = {'callback':'fetchJSON_comment98vv116',
              'productId':sku_group,
              'score':0,
              'sortType':6,
              'page':0,
              'pageSize':10,
              'isShadowSku':0}
    try:
        txt = requests.get(url, params=params).text
        comment_dict = json.loads(txt[25:-2]) #截取长度和fetchJSON_comment98vv116有关
        pages = comment_dict['maxPage']
    except:
        print('error: get_pages: %s' % sku_group)
        pages = 0
    return pages

#下载sku_group的第page页评论文本，若失败返回空值
def load(sku_group, page):
    url = 'https://club.jd.com/comment/productPageComments.action'
    params = {'callback':'fetchJSON_comment98vv116',
              'productId':sku_group,
              'score':0,
              'sortType':6,
              'page':page,
              'pageSize':10,
              'isShadowSku':0}
    try:
        response = requests.get(url, params=params)
        txt = response.text
    except:
        print('error: load: %s第%s页下载失败' % (sku_group, page))
        txt = ''
    return txt

#解析下载的内容
def parse(txt):
    crawl_date = datetime.date.today()
    now = datetime.datetime.now()
    crawl_time = now.strftime('%H:%M:%S')
    comment_dict = json.loads(txt[25:-2])
    image_list_count = comment_dict['imageListCount']
    comments = comment_dict['comments']
    comments_list = []
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
    return comments_list

#存入数据库
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', 
                           db='customer', charset='utf8') #设置编码格式
    cur = conn.cursor()
    sql = 'insert into comment_jd(category_level3_id, brand_id, sku_group, max_page,\
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
        print('error: input_mysql: 存入数据库失败%s' % record)
        pass
    cur.close()
    conn.close()
    
#主函数
def main():
    category_level3_id = '11729,11730,12066'
    brand_id = '101344'                                           #1.类别-品牌
    sku_group_list = get_sku_group(category_level3_id, brand_id) #2.sku列表
    if len(sku_group_list) > 0:                                  #3.sku列表不为空
        for sku_group in sku_group_list['sku_group']:            #4.遍历sku
            pages = get_pages(sku_group)                         #5.sku的评论页数
            if pages > 0:                                        #6.页数存在
                for page in range(0, pages):                     #7.遍历每页
                    print('%s--%s已完成%s/%s个SKU，%s已完成%s/%s页' %\
                    (category_level3_id, brand_id,\
                    list(sku_group_list['sku_group']).index(sku_group)+1,\
                    len(sku_group_list), sku_group, page + 1, pages))
                    txt = load(sku_group, page)                  #8.下载网页
                    comments_list = parse(txt)                   #9.解析数据，得到评论列表
                    for comment in comments_list:                #10.遍历每条评论
                        record = [category_level3_id, brand_id,  #11.构造表记录
                                  sku_group, pages, page] + comment
                        input_mysql(record)                      #12.存入数据库

if __name__ == '__main__':
    main()
