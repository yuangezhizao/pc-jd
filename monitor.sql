#sku_jd
select * from sku_jd order by id desc limit 10;
select * from sku_jd where crawl_date='2017-04-05' and page_size>6 order by id desc limit 10 #检查重定向是否有问题

#comment_count_jd
select * from comment_count_jd order by id desc limit 10;

#price_history_jd
select * from price_history_jd order by id desc limit 10;

#shop_jd
select * from shop_jd order by id desc limit 10;

#comment_jd_score_1
select * from comment_jd_score_1 order by id desc limit 10