# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 18:08:04 2016
http://item.m.jd.com/product/2292154.html
@author: Administrator
"""

import requests
import bs4
import re
import pymysql
import queue
import datetime

def parse(text,sku):
    global crawl_id
    sku_name = ''
    sku_price = ''
    stock_state = ''  
    service_provider = '' 
    ware_provider = ''
    shop_id = ''
    shop_name = ''
    shop_score = ''
    follow_count = ''
    vender_type = ''
    ware_type = ''
    diamond = ''
    ware_score = ''
    avg_ware_score = ''
    ware_score_level = ''
    efficiency_score = ''
    avg_efficiency_score = ''
    efficiency_score_level = '' 
    service_score = ''
    avg_service_score = ''
    service_score_level = ''
    crawl_date = datetime.datetime.today()
    now = datetime.datetime.now()
    crawl_time = now.strftime('%H:%M:%S')
    soup = bs4.BeautifulSoup(text,'html.parser')
    try:
        sku_name = soup.find('input',id='goodName').get('value')
        sku_price = soup.find('input',id='jdPrice').get('value')
        stock_state = re.findall("(?<=stockState:').+(?=')", text)[0]
        service_provider = soup.find('div',id='serviceFlag').get('data')
        try:
            ware_provider = soup.select('.title-text')[0].i.span.string
            #shop message
            shop_msg = re.findall("(?<=WareArg\['shopInfo'\] = ).+(?=;)", text)[0]
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
            service_score = shop['shopInfo']['shop']['serviceScore']
            avg_service_score = shop['shopInfo']['shop']['avgServiceScore']
            service_score_level = shop['shopInfo']['shop']['serviceScoreLevel']
        except:
            pass
    except:
        pass
    price_msg = [crawl_id,sku,sku_name,sku_price,stock_state,shop_id,shop_name,shop_score,
                 follow_count,vender_type,ware_type,diamond,ware_score,
                 avg_ware_score,ware_score_level,efficiency_score,
                 avg_efficiency_score,efficiency_score_level,service_score,
                 avg_service_score,service_score_level,service_provider,ware_provider,crawl_date,crawl_time]
    return price_msg
    
if __name__ == '__main__':
    crawl_id = input('please input crawl_id:')
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer')
    cur = conn.cursor()
    cur.execute('select sku from sku_jd limit 10')
    cur.close()
    conn.close()
    skus = cur.fetchall()
    sku_queue = queue.Queue()
    for i in skus:
        for j in i:
            sku_queue.put(j)
    while sku_queue.qsize()>0:
        sku = sku_queue.get()
        url = 'http://item.m.jd.com/product/'+str(sku)+'.html'
        headers = {'Cookie':'JAMCookie=true; __jda=122270672.852353802.1474856712.1477301199.1477356921288.27;\
        unpl=V2_ZzNtbRZeRBF3CRZQK0laV2IDFApKUhEVdglEBn8YDwxuVxNYclRCFXIURlVnGlkUZwUZXktcQhdFCHZXchBYAWcCGllyBBNNIEwHDCRSBUE3XHxcFVUWF3RaTwEoSVoAYwtBDkZUFBYhW0IAKElVVTUFR21yVEMldQl2XX8aXgFlChNecmdEJUU4QlV%2bG1oCVwIiXHIVF0l8DkRdfB8RDGMAEFlAXkIWRQl2Vw%3d%3d;\
        __jdv=122270672|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_e86530a5aa7c417f94c1203c50b88e04|1477301199403;\
        __jdu=852353802; ipLoc-djd=1-72-4137-0; areaId=1; ipLocation=%u5317%u4EAC; abtest=20161005102034069_20;\
        USER_FLAG_CHECK=246ece1006c1834c347f96e5d789b4c5; warehistory="2292154,206789,1080100340,1070599126,10607783015,10669879187,1079732539,10557525548,1079732545,1080100346,1624969,10186677059,1356559,10651853750,10607573177,10511132390,3367424,2526473,1492875010,1759267079,";\
        user-key=e1b9bd27-7f9b-476f-bec7-11c5e2bc551c; cn=0;\
        mt_xid=V2_52007VwoWUV9cUFMeSikMVWdRG1FYD05TS00fQAA3CxRODlBTUwNKHA5RYAQSUFVbVgkvShhcAnsDE05eWENaHEIdXQ5lAiJQbVhiWh1AH1oAZgUiUlheVQ%3D%3D;\
        downloadAppPlugIn_downCloseDate_downloadBM=1476928721482_259200000;\
        mobilev=html5; mba_muid=852353802; sid=55766492fb319ce3654811c03500b857; __jdb=122270672.1.852353802|27.1477356921288;\
        __jdc=122270672; mba_sid=14773569212966021617429660064.1'}
        txt = requests.get(url, headers=headers).text
        price = parse(txt,sku)
        conn = pymysql.connect(host='127.0.0.1', user='root', password='1111', db='customer', charset='utf8')
        cur = conn.cursor()
        sql = 'insert into price_jd(crawl_id,sku,sku_name,sku_price,stock_state,\
        shop_id,shop_name,shop_score,follow_count,vender_type,ware_type,\
        diamond,ware_score,avg_ware_score,ware_score_level,efficiency_score,\
        avg_efficiency_score,efficiency_score_level,service_score,\
        avg_service_score,service_score_level,service_provider,ware_provider,\
        crawl_date,crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(sql,price)
        conn.commit()
        