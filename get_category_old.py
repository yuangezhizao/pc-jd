# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 16:49:08 2016
抓取京东商品类别，旧版
@author: thinkpad
"""
import requests
import json

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