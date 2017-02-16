# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 21:35:13 2016
一、功能
根据京东商品类别（category_level3_id）和品牌(brand_id)，抓取全部的SKU

二、逻辑
1.获取待抓取的商品类别和品牌
（1）从category_jd获取所有的商品类别-品牌
（2）从sku_jd获取已抓取的商品类别-品牌
（3）从（1）和（2）得到待抓取的商品类别-品牌
2.抓取1中商品类别-品牌的所有SKU
https://list.jd.com/list.html?cat=1319,11842,11232&ev=exbrand_70562&page=6&stock=0&sort=sort_totalsales15_desc&trans=1

https://list.jd.com/list.html?
cat=737,794,798  #三级类别编码
&ev=exbrand_6742  #品牌编码 或 按尺寸、产品类型
&page=1  #页码
&stock=0  #无货也显示，若仅显示有货，则无此参数
&sort=sort_totalsales15_desc  #按销量降序排序，其他：sort_dredisprice_asc价格升序，sort_commentcount_desc评论数量降序，sort_winsdate_desc上架时间降序
&trans=1

三、禁爬规则
1.重定向
2.cookie
"""

import requests
import bs4
import pymysql
import datetime
import pandas as pd

#获取爬取顺序，返回category_level3_id和数量
def get_category():
    category_level3_ids = []
    category = pd.read_csv('C:/Users/Administrator/Documents/GitHub/pc-jd/crawl_order.csv', 
                           encoding='gbk')
    category.sort_values(by='category_level3_order', inplace=True)
    for i in category['category_level3_id']:
        category_level3_ids.append(i.split('"')[1])
    n = len(category_level3_ids)
    return category_level3_ids, n

#获取待抓取的品牌，返回brand_id和数量
def get_brand(category_level3_id):
    conn = pymysql.connect(host='127.0.0.1',user='root',password='1111',db='customer',charset='utf8')
    #全部品牌
    sql_all = 'select distinct brand_id\
               from category_jd\
               where crawl_id=(select crawl_id from category_jd order by id desc limit 1)\
               and category_level3_id="%s"' % category_level3_id
    brand_all = pd.read_sql(sql_all, conn)
    brand_all_list = []
    for b in brand_all['brand_id']:
        brand_all_list.append(b)
    #已爬取SKU的品牌
    sql_crawled = 'select distinct brand_id\
                   from sku_jd\
                   where crawl_id=(select crawl_id from sku_jd order by id desc limit 1)\
                   and category_level3_id="%s"' % category_level3_id
    brand_crawled = pd.read_sql(sql_crawled, conn)
    conn.close()
    brand_crawled_list = []
    for b in brand_crawled['brand_id']:
        brand_crawled_list.append(b)
    #未爬取SKU的品牌
    brand_ids = [b for b in brand_all_list if b not in brand_crawled_list]
    n = len(brand_ids)
    return brand_ids, n

#获取该品牌sku的页数，若失败返回0
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

#获取第page页的网页，失败返回空文本
def load(category_level3_id, brand_id, page):
    url = 'https://list.jd.com/list.html'
    params = {'cat' : category_level3_id,
              'ev' : 'exbrand_%s' % brand_id,
              'page' : page,
              'stock' : 0,
              'sort' : 'sort_totalsales15_desc',
              'trans' : 1}
    try:
        '''
        headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding':'gzip, deflate, br',
                   'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Connection':'keep-alive',
                   'Cookie':'__jda=122270672.852353802.1474856712.1480756815.1480900510.78; unpl=V2_ZzNtbUNVREJ9XUVXLhwPUmICFgpKUBdGJwxAV3MZWwYzBkFaclRCFXIURldnGF4UZwUZXkBcQRZFCHZWfBtaDFcKFVhGVkB7JzhHVSQaVQxnUBtdFgAQFCVfRFF6EGwGZzMabUtTQBdxCk9VeClsAlczSQgsUEpAdQBAUygYCwJjASJaR1FDF3MPRWR6KV01LG0TEEtTQBdxCk9VeCldNWQ%3d;\
                             __jdv=122270672|p.egou.com|t_36378_864502_c|tuiguang|036f9d22d4bf405f96ebc5729162e4b6|1480756814719;\
                             __jdu=852353802; ipLoc-djd=1-72-2799-0; listck=381760383d62bcb8e9656ed6a5c94049;\
                             ipLocation=%u5317%u4EAC; _jrda=1; 3AB9D23F7A4B3C9B=YESGQBZWR37GJSKUFLDQN2IMUQMBRII6WWPNUZGWF5IIS2DZNOKU3NVS7D6P6ZNKS5J57BJYANIQ4ITV4TGYT7P6WM;\
                             user-key=9ebf4812-8190-44f7-bb0b-0fe52e0430b4; cn=0; samoye_faved1=""; samoye_attentioned1="";\
                             __jdb=122270672.5.852353802|78.1480900510; __jdc=122270672',
                   'Host':'list.jd.com',
                   'Upgrade-Insecure-Requests':'1',
                   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        '''
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
        print('get_sku-error: load: %s-%s第%s页' % (category_level3_id, brand_id, page))
    return txt

#解析网页获取sku列表，失败返回空值
def parse(txt):
    sku_list = []
    soup = bs4.BeautifulSoup(txt, 'html.parser')
    try:
        for s in soup.select('div[venderid]'):
            sku_group = s['data-sku']
            vender_id = s['venderid']
            shop_id = s['jdzy_shop_id']
            try:
                sku_name = s.select('.p-name')[0].a.em.string
            except:
                sku_name = ''
            sku_list.append([sku_group, sku_name, vender_id, shop_id])
    except:
        sku_group = []
        print('get_sku-error: parse')
    return sku_list

#存入数据库
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1',user='root',password='1111',db='customer',charset='utf8')
    cur = conn.cursor()
    sql='insert into sku_jd(crawl_id, category_level3_id, brand_id, sku_group,\
         sku_name, vender_id, shop_id, page_index, page_size, crawl_date,\
         crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql, record)
        conn.commit()
    except:
        print('get_sku-error: input_mysql: 存入数据库失败%s' % record)
        pass
    cur.close()
    conn.close()

#爬取主函数
def crawl(crawl_id):
    #获取category_level3_id，若没有，则全部完成
    category_level3_ids, n1 = get_category()
    if len(category_level3_ids) > 0:
        for category_level3_id in category_level3_ids:
            #获取brand_id，若没有，则该品牌完成
            brand_ids, n2 = get_brand(category_level3_id)
            if len(brand_ids) > 0:
                for brand_id in brand_ids:
                    print('get_sku:品类已完成%s/%s，%s已完成%s/%s品牌' %\
                           ((category_level3_ids.index(category_level3_id)+1), n1,\
                           category_level3_id, (brand_ids.index(brand_id)), n2))
                    #获取品牌的页数，若页数大于0，则爬取
                    pages = get_pages(category_level3_id, brand_id)
                    crawl_date = datetime.date.today()
                    now = datetime.datetime.now()
                    crawl_time = now.strftime('%H:%M:%S')
                    if pages > 0:
                        #依次爬取每页
                        for page in range(1, pages+1):
                            txt = load(category_level3_id, brand_id, page)
                            now = datetime.datetime.now()
                            crawl_time = now.strftime('%H:%M:%S')
                            if txt != '':
                                sku_list = parse(txt)
                                if len(sku_list) > 0:
                                    for sku in sku_list:
                                        record = [crawl_id, category_level3_id, brand_id] +\
                                                 sku + [page, pages, crawl_date, crawl_time]
                                        input_mysql(record)
                    else:
                        record = [crawl_id, category_level3_id, brand_id, '', '',\
                                  '', '', 0, 0, crawl_date, crawl_time]
                        input_mysql(record)
            else:
                print('get_sku:%s所有品牌已完成' % category_level3_id)
    else:
        print('get_sku:所有品类已完成')


if __name__=='__main__':
    crawl_id=input('请输入抓取编号（如201609）：')
    crawl(crawl_id)

    
        
        
        
        
        
        
        
        
        
        
        
        

