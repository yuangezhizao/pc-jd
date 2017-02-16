# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 16:22:30 2017
1.功能
根据sku_jd中的shop_id抓取shop的自营、评分等信息
2.逻辑
（1）从sku_jd获取shop_jd
（2）下载shop的网页
（3）解析网页
（4）存入数据库
3.禁爬规则

@author: Administrator
"""

import requests
import pymysql
import pandas as pd
import bs4
import datetime

#获取shop_id及数量
def get_shop_id(crawl_id):
    conn = pymysql.connect(host='127.0.0.1',user='root',password='1111',db='customer',charset='utf8')
    #全部shop_id
    sql_all = 'select distinct shop_id from sku_jd\
               where crawl_id=(select crawl_id from sku_jd order by id desc limit 1)'
    shop_all = pd.read_sql(sql_all, conn)
    shop_all_list = []
    for i in shop_all['shop_id']:
        shop_all_list.append(i)
    #已爬取的shop_id
    sql_crawled = 'select distinct shop_id from shop_jd where crawl_id=%s' % crawl_id
    shop_crawled = pd.read_sql(sql_crawled, conn)
    shop_crawled_list = []
    for i in shop_crawled['shop_id']:
        shop_crawled_list.append(i)
    #未爬取的shop_id
    shop_ids = [i for i in shop_all_list if i not in shop_crawled_list]
    n = len(shop_ids)
    return shop_ids, n
    
#下载网页，若失败返回空文本
def load(shop_id):
    url = 'https://mall.jd.com/shopLevel-%s.html' % shop_id
    try:
        response = requests.get(url)
        txt = response.text
    except:
        print('get_shop-error-load:%s' % shop_id)
        txt = ''
    return txt

#解析网页，获取shop信息shop_msg
def parse(shop_id, txt):
    soup = bs4.BeautifulSoup(txt, 'html.parser')
    shop_name = soup.select('.j-shop-name')[0].string.strip()
    if len(shop_id) >= 10:
        is_zy = 1
    else:
        is_zy = 0
    #解析日期、时间
    crawl_date = datetime.date.today()
    now = datetime.datetime.now()
    crawl_time = now.strftime('%H:%M:%S')
    try:
        shop_msg_sub = parse_sub(txt)
    except:
        shop_msg_sub = ['',None, None, None, None, None, None, None, None,
                        None, None, None, None, None, None, None, None, None,
                        None, None]
    #shop_msg
    shop_msg = [shop_id, shop_name, is_zy] + shop_msg_sub + [crawl_date, crawl_time]
    return shop_msg

#解析网页，获取shop的次要信息shop_msg_sub，若失败置为空
def parse_sub(txt):
    soup = bs4.BeautifulSoup(txt, 'html.parser')
    location = soup.select('.j-shop-info')[0].select('.value')[0].string
    total_score = float(soup.select('.total-score-num')[0].span.string.split(' ')[0])
    #获取正负符号
    flag_txt = str(soup.select('.total-score-view')[0])
    flag_soup = bs4.BeautifulSoup(flag_txt, 'html.parser')
    flag_list = flag_soup.div['class']
    if 'red' in flag_list:
        flag = 1
    elif 'green' in flag_list:
        flag = -1
    else:
        flag = 0        
    total_score_percent = flag * float(str(flag_soup.select('.percent')[0].string).replace('%', ''))
    #180天内店铺动态评分
    score_180_list = []
    flag_180_list = [] #正负符号列表
    percent_180_list = []
    list_180 = soup.select('.item-180')
    for i in list_180:
        try:
            i_score = float(i.select('.score-180')[0].string.split(' ')[0])
        except:
            i_score = None
        score_180_list.append(i_score) #评分列表
        if i.div['class'][0] == 'red':
            flag_180 = 1
        elif i.div['class'][0] == 'green':
            flag_180 = -1
        else:
            flag_180 = 0
        flag_180_list.append(flag_180) #正负符号列表
        try:
            percent_180 = float(str(i.select('.percent')[0].string).replace('%', ''))
        except:
            percent_180 = None
        percent_180_list.append(percent_180)
    ware_score = score_180_list[0]
    try:
        ware_score_percent = flag_180_list[0] * percent_180_list[0]
    except:
        ware_score_percent = None
    service_score = score_180_list[1]
    try:
        service_score_percent = flag_180_list[1] * percent_180_list[1]
    except:
        service_score_percent = None
    logistics_score = score_180_list[2]
    try:
        logistics_score_percent = flag_180_list[2] * percent_180_list[2]
    except:
        logistics_score_percent = None
    description_score = score_180_list[3]
    try:
        description_score_percent = flag_180_list[3] * percent_180_list[3]
    except:
        description_score_percent = None
    return_score = score_180_list[4]
    try:
        return_score_percent = flag_180_list[4] * percent_180_list[4]
    except:
        return_score_percent = None
    #90天内平台监控店铺服务
    data_90_self_list = []
    data_90_others_list = []
    self_list_90 = soup.select('.service-des-self')
    for i in self_list_90:
        i_data = str(i.select('.f16')[0].string).replace('h', '')
        i_data = float(i_data.replace('%', ''))
        data_90_self_list.append(i_data)
    others_list_90 = soup.select('.service-des-others')
    for i in others_list_90:
        i_data = str(i.select('.f16')[0].string).replace('h', '')
        i_data = float(i_data.replace('%', ''))
        data_90_others_list.append(i_data)
    return_duration = data_90_self_list[0]
    return_duration_avg = data_90_others_list[0]
    dispute_ratio = data_90_self_list[1]
    dispute_ratio_avg = data_90_others_list[1]
    repair_ratio = data_90_self_list[2]
    rapair_ratio_avg = data_90_others_list[2]
    #店铺违法违规信息
    illegal_times = int(soup.select('.hegui-info')[0].a.string)
    #shop_msg_sub
    shop_msg_sub = [location, total_score, total_score_percent, ware_score, 
                    ware_score_percent, service_score, service_score_percent,
                logistics_score, logistics_score_percent, description_score,
                description_score_percent, return_score, return_score_percent,
                return_duration, return_duration_avg, dispute_ratio, dispute_ratio_avg,
                repair_ratio, rapair_ratio_avg, illegal_times]
    return shop_msg_sub

    
#存入数据库
def input_mysql(record):
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer', charset='utf8')
    cur = conn.cursor()
    sql = 'insert into shop_jd(crawl_id, shop_id, shop_name, is_zy, location, total_score,\
           total_score_percent, ware_score, ware_score_percent, service_score,\
           service_score_percent, logistics_score, logistics_score_percent, description_score,\
           description_score_percent, return_score, return_score_percent, return_duration,\
           return_duration_avg, dispute_ratio, dispute_ratio_avg, repair_ratio,\
           rapair_ratio_avg, illegal_times, crawl_date, crawl_time)\
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        cur.execute(sql, record)
        conn.commit()
        cur.close()
        conn.close()
    except:
        print('get_shop_jd-error-input_mysql: %s' % record)
        cur.close()
        conn.close()

#爬取主函数
def crawl(crawl_id):
    shop_ids, n1 = get_shop_id(crawl_id)
    if n1 > 0:
        for shop_id in shop_ids:
            print('get_shop_jd已完成%s/%s店铺' % ((shop_ids.index(shop_id) + 1), n1))
            txt = load(shop_id)
            if txt != '':
                try:
                    shop_msg = parse(shop_id, txt)
                    record = [crawl_id] + shop_msg
                    input_mysql(record)
                except:
                    print('get_shop_jd-error-parse:%s' % shop_id)
    else:
        print('get_shop_jd:全部完成')

if __name__ == '__main__':
    crawl_id = input('输入抓取编号：')
    crawl(crawl_id)

















