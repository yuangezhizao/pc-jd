# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 17:58:41 2015

@author: 14020199
"""

import requests
import bs4
import json
import pickle
proxies={'http':'http://10.19.110.31:8080'}
#step1:抓取类目编码和名字，保存为字典，形如：‘12259,12260,9435’:'白酒'
def category():
    category_list={}
    category_string=[]
    category_url='http://dc.3.cn/category/get?callback=getCategoryCallback'
    category_response=requests.get(category_url,proxies=proxies).text
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
#step2:构造类目的url，并抓取该类目的页面数量，保存为字典
def category_url():
    url={}
    #构造类目url的第一页
    url_base='http://list.jd.com/list.html?cat='
    category_list=category()
    for cat in category_list:
        cat_split=cat.split(',')
        if len(cat_split)==3:
            url_full=url_base+cat_split[0]+'%2C'+cat_split[1]+'%2C'+cat_split[2]+'&page=1&JL=6_0_0'
        elif len(cat_split)==2:
            url_full=url_base+cat_split[0]+'%2C'+cat_split[1]+'&page=1&JL=6_0_0'
        else:
            continue
        #抓取类目页面数量
        response=requests.get(url_full,proxies=proxies).text
        soup=bs4.BeautifulSoup(response,'html.parser')
        span=soup.select('.fp-text')#查找class='fp-text'的标签
        url[url_full]=int(span[0].i.string)
    return url
b=category_url()
file=open('d:/category.pkl','wb')
pickle.dump(b,file,True)
file.close()

file2=open('d:/category.pkl','rb')
b1=pickle.load(file2)
file2.close()

url_rest=[]
for u in b1:
    pages=b1[u]
    for page in range(1,pages+1):
        url_trans=u.replace('page=1','page='+str(page))
        url_rest.append(url_trans)
file3=open('d:/url_rest.pkl','wb')
pickle.dump(url_rest,file3,True)
file3.close()
