# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 13:28:21 2016 @南京图书馆
一、功能
抓取京东商品类别，并存入数据库
[三级类别编码，三级类别名称，二级类别名称，一级类别名称]
[737,738,751，电风扇，生活电器，家用电器]
二、逻辑
1.首页商品目录（building--storey--catalog）
    全部商品分类：【catalog 目录】
    1.家用电器 【catalog_level1 一级目录】
      1.1 电视 【catalog_level2 二级目录】
        1.1.1 合资品牌 【catalog_level3 三级目录】
        1.1.2 国产品牌
        1.1.3 互联网品牌
      1.2 空调
      ...
      1.9 家庭影音
    2.手机、数码、京东通信
    3.电脑、办公
    ...
    15.理财、众筹、白条、保险 【共15层】
2.商品目录转换成商品类别【catalog-->category】
（1）如果二级目录编码是“737,794,870”形式，那么三级类别编码=二级目录编码，三级类别名称=二级目录名称，二级类别名称=二级目录名称，一级类别名称=一级目录名称
（2）否则，如果三级目录编码是“737,794,870”形式，那么三级类别编码=三级目录编码，三级类别名称=三级目录名称，二级类别名称=二级目录名称，一级类别名称=一级目录名称
（3）否则，如果三级目录编码是“6196-6197”形式，那么向下爬http://channel.jd.com/6196-6197.html获取三级类别编码和名称，二级类别名称=三级目录名称，一级类别名称=一级目录名称
3.商品目录URL：http://dc.3.cn/category/get?callback=getCategoryCallback
@author: thinkpad
"""

import requests
import json

def get_category():
    storeys_url='http://dc.3.cn/category/get?callback=getCategoryCallback'      #京东首页目录楼层地址
    response=requests.get(storeys_url).text                                     #？错误捕捉与处理
    storeys_json=json.loads(response[20:-1])
    storeys=storeys_json['data']                                                #目录楼
    storeys_num=len(storeys)                                                     #层数，每层包含若干目录
    for i in range(0,1):                                                        #遍历目录楼
        storey=storeys[i]                                                        #第i层目录楼
        catalogs_level1=storey['s']                                              #第i层的所有一级目录
        for j in range(0,len(catalogs_level1)):                                 #遍历一级目录
            catalog_level1=catalogs_level1[j]                                   #第i层的第j个一级目录
            catalog_level1_name=catalog_level1['n'].split('|')[1]               #第j个一级目录名称
            catalogs_level2=catalog_level1['s']                                 #第j个一级目录的所有二级目录
            for k in range(0,len(catalogs_level2)):                                 #遍历二级目录
                catalog_level2=catalogs_level2[k]                               #第j个一级目录的第k个二级目录
                catalog_level2_n=catalog_level2['n']
                print(catalog_level2_n)
            
                
        
        
        
        
        
    
    
    


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