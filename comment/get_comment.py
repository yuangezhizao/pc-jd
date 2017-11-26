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
import gevent
from gevent import monkey
gevent.monkey.patch_all(thread=False)


