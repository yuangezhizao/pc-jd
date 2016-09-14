create table category_jd(           #京东类别全量表
  crawl_id char(6) not null,        #抓取编号
  category_level3_id varchar(45),   #三级类别编码
  category_level3_name varchar(90), #三级类别名称
  category_level2_name varchar(90), #二级类别名称
  category_level1_name varchar(90), #一级类别名称
  crawl_date varchar(45)            #抓取日期
);
create table sku_jd(                #京东sku全量表
  crawl_id char(6) not null,        #京东抓取编号
  sku varchar(45),                  #sku编码
  sku_group varchar(45),            #sku组名,如相同款式衣服，不同的颜色
  category_level3_id varchar(45),   #三级类别编码
  crawl_date varchar(45),           #抓取日期
  crawl_time varchar(45));          #抓取时间