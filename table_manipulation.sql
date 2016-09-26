create table category_jd(           #京东类别全量表
  crawl_id char(6) not null,        #抓取编号
  category_level3_id varchar(45),   #三级类别编码
  category_level3_name varchar(90), #三级类别名称
  category_level2_name varchar(90), #二级类别名称
  category_level1_name varchar(90), #一级类别名称
  crawl_date varchar(45)            #抓取日期
);
create table sku_jd(                #京东sku全量表
  id bigint auto_increment primary key, #自增主键
  crawl_id char(6) not null,        #京东抓取编号
  sku varchar(45),                  #sku编码
  sku_group varchar(45),            #sku组名,如相同款式衣服，不同的颜色
  category_level3_id varchar(45),   #三级类别编码
  crawl_date varchar(45),           #抓取日期
  crawl_time varchar(45));          #抓取时间
create table comment_count_jd(      #京东商品评论数量表
  id bigint auto_increment primary key, #自增主键
  crawl_id char(6) not null,        #抓取编号
  sku_group varchar(45),            #sku_jd.sku_group
  score1_count int,                 #1分评论数量
  score2_count int,                 #2分评论数量
  score3_count int,                 #3分评论数量
  score4_count int,                 #4分评论数量
  score5_count int,                 #5分评论数量
  show_count int,                   #
  comment_count int,                #评论总数量
  average_score decimal(3,1),       #平均评分
  good_count int,                   #好评数量
  good_rate decimal(5,3),           #好评比例
  good_rate_show int,
  good_rate_style int,
  general_count int,                #中评数量
  general_rate decimal(5,3),        #中评比例
  general_rate_show int,
  general_rate_style int,
  poor_count int,                   #差评数量
  poor_rate decimal(5,3),           #差评比例
  poor_rate_show int,
  poor_rate_style int,
  crawl_date varchar(45),
  crawl_time varchar(45)) engine=InnoDB;

