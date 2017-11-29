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



def load(sku, page, score=0, sort_type=6):
    url = 'https://club.jd.com/comment/skuProductPageComments.action'
    params = {'productId':sku,
              'score':score,
              'sortType':sort_type,
              'page':page,
              'pageSize':10,
              'isShadowSku':0}
    try:
        response = requests.get(url, params=params)
        txt = response.text
    except:
        print('error: load: %s第%s页下载失败' % (sku, page))
        txt = ''
    return txt
    