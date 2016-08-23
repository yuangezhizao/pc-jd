# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 13:28:21 2016 @南京图书馆
抓取京东品类,url='http://dc.3.cn/category/get?callback=getCategoryCallback'

@author: thinkpad
"""

import requests
import json

def get_category():
    catalog_url='http://dc.3.cn/category/get?callback=getCategoryCallback' #京东首页目录
    '''
    全部商品分类：
    1.家用电器
      1.1 电视
        1.1.1 合资品牌
        1.1.2 国产品牌
        1.1.3 互联网品牌
      1.2 空调
      ...
      1.9 家庭影音
    2.手机、数码、京东通信
    3.电脑、办公
    ...
    15.理财、众筹、白条、保险   
    '''
    response=requests.get(catalog_url).text      #？错误捕捉与处理
    catalog_json=json.loads(response[20:-1])
    catalog_list=catalog_json['data']#目录列表
    catalog_num=len(catalog_list)#目录数量，每个目录包含若干一级商品类别
    for i in range(0,1):
        catalog_i=catalog_list[i] #第i个目录
        catalog_i_list=catalog_i['s'] #列表
        for j in range(0,len(catalog_i_list)):
            category_level1=catalog_i_list[j]
            category_level1_name=category_level1['n'].split('|')[1] #一级类别名称
            category_level1_list=category_level1['s']
            for k in range(0,len(category_level1_list)):
                
        
        
        
        
        
    
    
    


'''
#step1:抓取类目编码和名字，保存为字典，形如：‘12259,12260,9435’:'白酒'
def get_category():
    category_list={}
    category_string=[]
    category_url='http://dc.3.cn/category/get?callback=getCategoryCallback'
    category_response=requests.get(category_url).text
    category_json=json.loads(category_response[20:-1])
    #解析json
    level1_data=category_json['data']
    len_level1=len(level1_data)
    for i in range(0,len_level1):
        level2_s=level1_data[i]['s']
        len_level2=len(level2_s)
        for j in range(0,len_level2):
            level3_s=level2_s[j]['s']
            len_level3=len(level3_s)
            for k in range(0,len_level3):
                level4_s=level3_s[k]['s']
                len_level4=len(level4_s)
                for l in range(0,len_level4):
                    level5_n=level4_s[l]['n']
                    if level5_n[0].isdigit():
                        category_string.append(level5_n)
                    else:
                        continue
    #规范化字符串
    for string in category_string:
        string_split=string.split('|')
        category_id=string_split[0].replace('-',',')
        category_name=string_split[1]
        category_list[category_id]=category_name
    return category_list
'''