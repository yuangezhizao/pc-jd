# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 13:04:44 2017
抓取指定SKU的评论
https://club.jd.com/comment/skuProductPageComments.action?productId=5089235&score=0&sortType=6&page=0&pageSize=10&isShadowSku=0
productId: sku
score: 1:差评 2：中评 3：好评 0：所有
sortType: 6:时间排序 5：推荐排序
page: 页码

@author: Administrator
"""

import requests
#import gevent
#from gevent import monkey
#gevent.monkey.patch_all(thread=False)
import datetime
import json
import logging

#日志
logger = logging.getLogger('get_comment')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('C:/Users/Administrator/Documents/GitHub/pc-jd/comment/logger.txt')
pattern = logging.Formatter('%(asctime)s-%(filename)s[line: %(lineno)d]-%(funcName)s-%(levelname)s-%(message)s')
handler.setFormatter(pattern)
logger.addHandler(handler)

#爬取sku第page页的评论，失败返回空list
#score: 1:差评 2：中评 3：好评 0：所有
#sort_type: 6:时间排序 5：推荐排序
def get_comment(sku, page, score=1, sort_type=6):
    url = 'https://club.jd.com/comment/skuProductPageComments.action'
    params = {'productId':sku,
              'score':score,
              'sortType':sort_type,
              'page':page,
              'pageSize':10,
              'isShadowSku':0}
    try:
        headers = {'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                   'Connection': 	'keep-alive',
                   'Cookie': '__jda=122270672.1510146318720515461731.1510146319.1512050551.1512132566.14; \
                              __jdu=1510146318720515461731; ipLoc-djd=1-72-4137-0; \
                              areaId=1; user-key=5e1e3763-7d5d-4469-87df-172337fd4f04; \
                              cn=0; __jdv=122270672|direct|-|none|-|1511673043164; \
                              __jdb=122270672.3.1510146318720515461731|14.1512132566; \
                              __jdc=122270672; seckillSku=5089253; seckillSid=; \
                              3AB9D23F7A4B3C9B=Y6IKLRFYDNP2G3YYGCQ3OPP56J5EWHCRSFC7B5EJ7KJOE3C2W64HZIGIYMTYYBVXG6AEPRMVAQMP74IX7DQK5SYHRA',
                   'Host': 'club.jd.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
        response = requests.get(url, params=params, headers=headers)
        txt = response.text
        comments_list = parse(txt)
        logger.info('成功获取%s第%s页的%s条评论' % (sku, page, len(comments_list)))
    except:
        logger.error('%s第%s页评论获取失败' % (sku, page))
        comments_list = []
    return comments_list


#返回评论list，若没有评论返回空list
def parse(txt):
    now = datetime.datetime.now()
    crawl_time = now.strftime('%Y-%m-%d %H:%M:%S')
    comment_dict = json.loads(txt)
    image_list_count = comment_dict.get('imageListCount', -1)
    comments = comment_dict['comments']
    comments_list = []
    if len(comments) > 0:
        for i in range(0, len(comments)):
            comment = comments[i]
            comment_id = comment.get('id', 0)
            content = comment.get('content', '') 
            creation_time = comment.get('creationTime', '')
            reference_time = comment.get('referenceTime', '')
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
            image_dict = {}
            images = comment.get('images', [])
            if len(images):
                for image in images:
                    image_dict[image['id']] = image['imgUrl']
            img_url = json.dumps(image_dict, ensure_ascii=False)       
            comment_i = [image_list_count, comment_id, content, creation_time, 
                         reference_time, reply_count, score, useful_vote_count,
                         user_image_url, user_level_id, user_province, 
                         user_register_time, nickname, product_color,
                         product_size, image_count, anonymous_flag, user_level_name,
                         user_client_show, is_mobile, days, img_url, crawl_time]
            comments_list.append(comment_i)  
    return comments_list




    