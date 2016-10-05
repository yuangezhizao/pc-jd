# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 11:03:27 2016
一、功能
抓取京东SKU价格，存入MYSQL
[id,crawl_id,sku,sku_name,sku_price,stock_state,shop_id,shop_name,shop_score,\
follow_count,vender_type,ware_type,diamond,ware_score,avg_ware_score,ware_score_level,\
efficiency_score,avg_efficiency_score,efficiency_score_level,service_score,\
avg_service_score,service_score_level,service_provider,ware_provider,crawl_date,crawl_time]
二、逻辑
手机端url='http://item.m.jd.com/product/2292154.html'

@author: lz
"""

import requests
import bs4
import re

def parse():
    url='http://item.m.jd.com/product/206789.html'
    response=requests.get(url).text
    soup=bs4.BeautifulSoup(response,'html.parser')
    sku_name = soup.find('input',id='goodName').get('value')
    sku_price = float(soup.find('input',id='jdPrice').get('value'))
    stock_state = re.findall("(?<=stockState:').+(?=')", response)[0]
    #shop message
    shop_msg = re.findall("(?<=WareArg\['shopInfo'\] = ).+(?=;)", response)[0]
    shop_msg = shop_msg.replace('true','"true"')
    shop_msg = shop_msg.replace('false','"false"')
    shop_msg = shop_msg.replace('null','"null"')
    shop = eval(shop_msg)
    shop_id = str(shop['shopInfo']['shop']['shopId'])
    shop_name = str(shop['shopInfo']['shop']['name'])
    shop_score = shop['shopInfo']['shop']['score']
    follow_count = shop['shopInfo']['shop']['followCount']
    vender_type = shop['shopInfo']['shop']['venderType']
    ware_type = shop['shopInfo']['shop']['wareType']
    diamond = shop['shopInfo']['shop']['diamond']
    ware_score = shop['shopInfo']['shop']['wareScore']
    avg_ware_score = shop['shopInfo']['shop']['avgWareScore']
    ware_score_level = shop['shopInfo']['shop']['wareScoreLevel']
    
    efficiency_score = shop['shopInfo']['shop']['efficiencyScore']
    avg_efficiency_score = shop['shopInfo']['shop']['avgEfficiencyScore']
    efficiency_score_level = shop['shopInfo']['shop']['efficiencyScoreLevel']  
    
    return diamond