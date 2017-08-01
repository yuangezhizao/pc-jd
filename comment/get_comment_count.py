# -*- coding: utf-8 -*-
"""
一、功能
抓取sku_group的评分数量：
http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=sku
1.京东的精确评论数量不到每个SKU，到sku_group
2.抓取sku_group中每个sku的评论数量
3.取最大的sku评论数量作为sku_group的评论数量

二、禁爬规则
无
"""

import requests
import logging

#日志
logger = logging.getLogger('get_comment_count')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('C:/Users/Administrator/Documents/GitHub/pc-jd/comment/logger.txt')
pattern = logging.Formatter('%(asctime)s-%(filename)s[line: %(lineno)d]-%(funcName)s-%(levelname)s-%(message)s')
handler.setFormatter(pattern)
logger.addHandler(handler)

#返回评论总数和各评分数量
def get_comment_count(sku):
    url = 'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=%s' % sku
    #请求网页
    try:
        txt = requests.get(url).text
    except:
        logger.error('请求失败%s' % sku)
        txt = ''
    #解析
    try:
        count_dict=eval(txt) #转换成字典
        score1_count=count_dict['CommentsCount'][0]['Score1Count']
        score2_count=count_dict['CommentsCount'][0]['Score2Count']
        score3_count=count_dict['CommentsCount'][0]['Score3Count']
        score4_count=count_dict['CommentsCount'][0]['Score4Count']
        score5_count=count_dict['CommentsCount'][0]['Score5Count']
        comment_count=count_dict['CommentsCount'][0]['CommentCount']
        comments = []
        comments = [score1_count, score2_count, score3_count, score4_count, 
                    score5_count, comment_count]
    except:
        logger.error('解析失败%s' % sku)    
        comment_count = -1
        comments = [-1, -1, -1, -1, -1, -1]
    return comment_count, comments

    

            
        
