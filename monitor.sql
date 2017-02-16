#sku_jd
select * from sku_jd order by id desc limit 10;
select * from sku_jd where crawl_date='2017-02-09' and page_size>6 order by id desc limit 10 #检查重定向是否有问题

select * from comment_count_jd order by id desc limit 10;
select * from price_history_jd order by id desc limit 10;
select * from shop_jd order by id desc limit 10;
select * from comment_jd_score_1 order by id desc limit 10