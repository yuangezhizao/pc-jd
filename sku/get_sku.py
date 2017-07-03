# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 21:28:17 2017
爬sku:
1.根据category_level3_id, brand_id进入sku_group列表页
https://list.jd.com/list.html?cat=1319,11842,11232&ev=exbrand_70562&page=6&stock=0&sort=sort_totalsales15_desc&trans=1

https://list.jd.com/list.html?
cat=737,794,798  #三级类别编码
&ev=exbrand_6742  #品牌编码 或 按尺寸、产品类型
&page=1  #页码
&stock=0  #无货也显示，若仅显示有货，则无此参数
&sort=sort_totalsales15_desc  #按销量降序排序，其他：sort_dredisprice_asc价格升序，sort_commentcount_desc评论数量降序，sort_winsdate_desc上架时间降序
&trans=1

2.根据sku_group进入sku_group详情页，获取所有的sku
https://item.jd.com/3748771.html

3.根据sku进入sku详情页，获取sku的详细信息

"""
import requests
import bs4
import re
import json

sku_url = 'https://item.jd.com/%s.html'

#获取sku_group列表页的页数
def get_pages(category_level3_id, brand_id):
    url = 'https://list.jd.com/list.html'
    params = {'cat' : category_level3_id,
              'ev' : 'exbrand_%s' % brand_id,
              'page' : 1,
              'stock' : 0,
              'sort' : 'sort_totalsales15_desc',
              'trans' : 1}
    try:
        response = requests.get(url, params=params, allow_redirects=False)
        if response.status_code == 302:
            pages = 0
        else:
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            span = soup.select('.p-skip')
            result = soup.select('.result')
            if len(span) > 0:
                pages = int(span[0].em.b.string)
            elif len(result) > 0 and result[0].string == '抱歉，没有找到相关的商品':
                pages = 0
            else:
                pages = 1
    except:
        pages = 0
    return pages

#获取第page页的sku_group
def get_sku_group(category_level3_id, brand_id, page):
    sku_group_list = []
    url = 'https://list.jd.com/list.html'
    params = {'cat' : category_level3_id,
              'ev' : 'exbrand_%s' % brand_id,
              'page' : page,
              'stock' : 0,
              'sort' : 'sort_totalsales15_desc',
              'trans' : 1}
    try:
        headers = {'Host': 'list.jd.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Cookie': '__jda=122270672.852353802.1474856712.1486358489.1486431022.166;\
                              unpl=V2_ZzNtbUYCREd1C0UBK0pbA2JXRVRKXkYWcFhFXXpJCQViARBYclRCFXMUR1dnGFsUZwEZXkBcQhRFCHZXeBhYBmYBG1hyZ3MWdThOZHIdXwdjARtcQWdzEkU4OgowQQFYNwATXUdnQBZ0DEZdeRpaNWYzEFVLX0oUdg5GZDB3XUhuBxFfRlVKFHY4R2R4;\
                              __jdv=122270672|offlintab.firefoxchina.cn|t_220520384_|tuiguang|5d6c122dab674ef898424a280ad14334|1486358488626;\
                              __jdu=852353802; ipLoc-djd=12-904-3379-0; listck=6a4f06bc7909c0febd00a75cb624f2dd; ipLocation=%u6C5F%u82CF;\
                              TrackID=1xERLbwIsJ4vTcdDWgOt2SFQqRrEj1Nqfvz5rtXc3_ln4C2LGW_qJ-DuOBavxz5ZsGAbKgvPRB_AJM1VMRm3xF-20QzKQTm3zsaQa2n_HLj8;\
                              pinId=eEjGiU8n5xTiJ9euZLy0oQ; mt_xid=V2_52007VwoWUV9cUFMeSikMUm8AFlZbXE4NF0hKQABlBhVOVFtSUgMeGg9QYQFCBVhZVw0vShhcA3sCEk5eXUNZHkIYVQ5nCiJQbVhiWh5NEVsBZQcTYlhe;\
                              areaId=12; __jdb=122270672.4.852353802|166.1486431022;\
                              __jdc=122270672',
                   'Connection': 'keep-alive',
                   'Upgrade-Insecure-Requests': '1'}
        response = requests.get(url, params=params, headers=headers, allow_redirects=False)
        txt = response.text
    except:
        txt = ''
        print('error: get_sku_group: 下载%s的%s第%s页失败' % (category_level3_id, brand_id, page))
    if txt:
        soup = bs4.BeautifulSoup(txt, 'html.parser')
        for s in soup.select('div[venderid]'):
            sku_group = s['data-sku']
            sku_group_list.append(sku_group)
    else:
        sku_group_list = []
    return sku_group_list
        
    

#根据sku_group获取sku，失败返回空list
def get_sku_from_sku_group(sku_group):
    url = sku_url % sku_group
    try:
        txt = requests.get(url).text
        pattern = '(?<="skuId":)\d{3,}'
        sku_list = re.findall(pattern, txt)
    except:
        sku_list=[]
        print('error: get_sku_from_sku_group: %s' % sku_group) 
    return sku_list

#获取sku的参数
def get_sku_params(sku):
    url = sku_url % sku
    params = []
    specs_dict = {}
    try:
        txt = requests.get(url).text
        soup = bs4.BeautifulSoup(txt, 'html.parser')
        sku_name = soup.find('a', href='//item.jd.com/%s.html' % sku).string
        params.append(sku_name)
        vender_id = re.findall('(?<=venderId:)\d+(?=,)', txt)[0]
        params.append(vender_id)
        shop_id = re.findall("(?<=shopId:')\d+(?=')", txt)[0]
        params.append(shop_id)
        specs_soup = soup.select('.Ptable-item')
        for s in specs_soup:
            h3_name = s.h3.string
            specs_dict.setdefault(h3_name, {})
            dt_name = []
            dd_name = []
            for t in s.find_all('dt'):
                dt_name.append(t.string)
            for i in s.find_all('dd'):
                dd_name.append(i.string)
            for j in range(0, len(dt_name)):
                specs_dict[h3_name][dt_name[j]] = dd_name[j]
        specs = json.dumps(specs_dict, ensure_ascii=False)
        params.append(specs)
    except:
        print('error: get_sku_params: %s' % sku)
    return params

    

