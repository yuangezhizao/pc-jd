# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 16:19:20 2017
爬取品牌
1.根据category_level3_id
2.https://list.jd.com/list.html?cat=三级类别编码&trans=1&md=1&my=list_brand
3.没有禁爬
"""

import requests
import json
import datetime

#下载网页，若失败返回空文本
def load(category_level3_id):
    url = 'https://list.jd.com/list.html'
    params = {'cat' : category_level3_id,
              'trans' : 1,
              'md' : 1,
              'my' : 'list_brand'}
    try:
        response = requests.get(url, params=params)
        txt = response.text
    except:
        print('error: get_brand.load: %s' % category_level3_id)
        txt = ''
    return txt
    
#解析网页，返回品牌列表，若失败返回空
def parse(txt):
    brands_list = []
    try:
        txt_dict = json.loads(txt)
        catalog_level1_name = txt_dict['summary']['cate_infos']['cat1_name']
        catalog_level2_name = txt_dict['summary']['cate_infos']['cat2_name']
        catalog_level3_name = txt_dict['summary']['cate_infos']['cat3_name']
        brands = txt_dict['brands']
        now = datetime.datetime.now()
        crawl_time = now.strftime('%Y-%m-%d %H:%M:%S')
        if brands is not None:
            for brand in brands:
                brand_id = str(brand['id'])
                brand_name = brand['name']
                brand_record = [catalog_level3_name, catalog_level2_name,
                                catalog_level1_name, brand_id, brand_name, crawl_time]
                brands_list.append(brand_record)
        else:
            brands_list = []               
    except:
        brands_list = []
        print('error: get_brand.parse')
    return brands_list
    


