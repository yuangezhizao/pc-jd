# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 15:42:40 2017
一、功能
抓取有评论商品的历史价格
二、逻辑
1.获取待抓取的品类、品牌和SKU
（1）从crawl_order获取category_level3_ids
（2）通过category_level3_ids从comment_count_jd获取brand_sku（comment_count>10）
（3）从price_history_jd获取已抓取的brand_sku
（4）由（2）和（3）获取待抓取的brand_sku
2.下载网页
http://tool.manmanbuy.com/history.aspx?\
w=950
&h=580
&h2=420
&m=1
&e=1
&tofanli=0
&url=http://item.jd.com/10351869600.html
3.解析网页
4.存入数据库
三、禁爬规则
无
@author: Administrator
"""
import re 
import requests
import datetime
import pymysql
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

#获取待抓取的品牌-sku
def get_brand_sku(category_level3_id, crawl_id):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111',
                           db='customer', charset='utf8')
    #comment_count_jd所有的品牌-sku
    sku_all = []
    sql_all = 'select concat(brand_id, "-", sku_group) as sku\
               from comment_count_jd where crawl_id=(select crawl_id from comment_count_jd\
               order by id desc limit 1) and category_level3_id="%s"'\
               % category_level3_id #根据最新的crawl_id
    records_all = pd.read_sql(sql_all, conn)
    records_all = records_all.drop_duplicates('sku')
    for i in records_all['sku']:
        sku_all.append(i)
    #price_history_jd已爬取的品牌-sku
    sku_crawled = []
    sql_crawled = 'select concat(brand_id, "-", sku_group) as sku\
                   from price_history_jd where crawl_id=%s\
                   and category_level3_id="%s"' % (crawl_id, category_level3_id)
    records_crawled = pd.read_sql(sql_crawled, conn)
    records_crawled = records_crawled.drop_duplicates('sku')
    for i in records_crawled['sku']:
        sku_crawled.append(i)
    #未爬取的sku
    sku_task = [i for i in sku_all if i not in sku_crawled]
    sku_task.sort()
    n = len(sku_task)
    conn.close()
    return sku_task, n

#下载网页，若失败返回''
def load(sku_group):
    url = 'http://tool.manmanbuy.com/history.aspx'
    params = {'w':950,
              'h':580,
              'h2':420,
              'm':1,
              'e':1,
              'tofanli':0,
              'url':'http://item.jd.com/%s.html' % sku_group}
    try:
        response = requests.get(url, params=params)
        txt = response.text
    except:
        print('get_history_price-error: load: %s下载失败' % sku_group)
        txt = ''
    return txt

#解析网页，返回日期区间和价格
def parse(txt):
    interval_price = [] #日期区间-价格列表
    date_list = [] #日期列表
    interval_list = [] #日期的区间列表
    price_list = [] #价格列表
    data_string = re.findall('\[Date.+\]', txt)[0] #日期-价格字符串
    date_string = re.findall('(\d+,\d+,\d+)', data_string) #日期字符串
    price_string = re.findall('(?<=,)\d+\.\d+(?=])', data_string) #价格字符串
    #日期字符串转换成日期列表
    for i in date_string:
        i = i.replace(',', '-')
        date = datetime.datetime.strptime(i, '%Y-%m-%d').date()
        if date.month < 12:
            date = date.replace(month = date.month+1) #向后偏移一个月
        else:
            date = date.replace(year= date.year+1, month = 1) #12月向后偏1年
        date_list.append(date)    
    #日期列表转换成日期的区间列表
    for i in range(0, len(date_list)-1):
        date_begin = date_list[i]
        if date_list[i+1] == date_list[i]:
            date_end = date_list[i+1]
        else:
            date_end = date_list[i+1] - datetime.timedelta(1)
        interval_list.append([date_begin, date_end])
    #价格字符串转换成价格列表
    for i in price_string:
        price_list.append(float(i))
    #日期区间列表和价格列表合并成日期区间-价格列表
    for i in range(0, len(interval_list)):
        i_list = [j for j in interval_list[i]]
        i_list = i_list + [price_list[i]]
        interval_price.append(i_list)
    #部分日期是“2057-4-19”，需删除
    n = len(interval_price)
    if n > 1 and interval_price[n-1][1] > datetime.date.today():
        interval_price = interval_price[0:n-1]
    return interval_price

#存入数据库
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer')
    cur = conn.cursor()
    sql = 'insert into price_history_jd(crawl_id, category_level3_id, brand_id,\
           sku_group, date_begin, date_end, price, crawl_date, crawl_time)\
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql, record)
        conn.commit()
        cur.close()
        conn.close()
    except:
        print('get_history_price-error-input_mysql: %s' % record)
        cur.close()
        conn.close()

def crawl(crawl_id):
    category_level3_ids, n1 = get_category() #三级商品编码
    for category_level3_id in category_level3_ids:
        print('get_history_price:已完成%s/%s品类，当前品类：%s' %\
              ((category_level3_ids.index(category_level3_id)), n1, category_level3_id))
        brand_sku_list, n2 = get_brand_sku(category_level3_id, crawl_id) #品牌-sku
        if n2 > 0:
            for brand_sku in brand_sku_list:
                brand_id = brand_sku.split('-')[0]
                sku_group = brand_sku.split('-')[1]
                txt = load(sku_group)
                crawl_date = datetime.date.today()
                now = datetime.datetime.now()
                crawl_time = now.strftime('%H:%M:%S')
                if txt != '':
                    try:
                        interval_price = parse(txt)
                        for i in interval_price:
                            record = [crawl_id, category_level3_id, brand_id, sku_group]\
                                     + i + [crawl_date, crawl_time]
                            input_mysql(record)
                    except:
                        print('get_history_price-error: parse: %s' % sku_group)
                else:
                    continue
        else:
            print('get_history_price-crawl:%s over' % category_level3_id)


if __name__ == '__main__':
    crawl_id = input('输入抓取编号：')
    crawl(crawl_id)
    

















