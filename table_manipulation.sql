create table category_jd(           #京东类别全量表
  id int auto_increment primary key, #自增主键
  crawl_id char(6) not null,        #抓取编号
  brand_id varchar(15),             #品牌编号
  brand_name varchar(60),           #品牌名称
  category_level3_id varchar(20),   #三级类别编码
  category_level3_name varchar(45), #三级类别名称
  category_level2_name varchar(45), #二级类别名称
  category_level1_name varchar(45), #一级类别名称
  crawl_date varchar(15),            #抓取日期
  crawl_time varchar(15),            #抓取时间
  index(category_level3_id,brand_id),#两个索引
  index(crawl_id),
  index(category_level1_name),
  index(category_level3_name)
);
create table sku_jd(
  id int auto_increment primary key,#自增主键
  crawl_id char(6) not null,        #京东抓取编号
  category_level3_id varchar(20),   #category_jd.category_level3_id
  brand_id varchar(15),             #category_jd.brand_id 
  sku_group varchar(20),            #sku组名,如相同款式衣服，不同的颜色
  sku_name varchar(200),            #名称
  vender_id varchar(15),            #供应商编码
  shop_id varchar(15),              #店铺编码
  page_index smallint,              #sku所在的品类-品牌页码
  page_size smallint,               #页数
  crawl_date date,                  #抓取日期
  crawl_time time,                  #抓取时间
  index(crawl_id),
  index(category_level3_id),
  index(brand_id),
  index(shop_id),
  index(crawl_date)
  ) engine=InnoDB;          

create table comment_count_jd(      #京东商品评论数量表
  id int auto_increment,            #自增主键
  crawl_id char(6) not null,        #抓取编号
  category_level3_id varchar(20),   #category_jd.category_level3_id
  brand_id varchar(15),             #category_jd.brand_id
  sku_group varchar(20),            #sku_jd.sku_group
  score1_count int,                 #1分评论数量
  score2_count int,                 #2分评论数量
  score3_count int,                 #3分评论数量
  score4_count int,                 #4分评论数量
  score5_count int,                 #5分评论数量
  comment_count int,                #评论总数量
  crawl_date char(10),
  crawl_time char(8),
  primary key(id, crawl_id),
  index(category_level3_id), 
  index(brand_id),
  index(sku_group)
  ) engine=InnoDB
  partition by list columns(crawl_id)
  (
  partition p00 values in ('201612'),
  partition p01 values in ('201701'),
  partition p02 values in ('201702'),
  partition p03 values in ('201703'),
  partition p04 values in ('201704'),
  partition p05 values in ('201705'),
  partition p06 values in ('201706'),
  partition p07 values in ('201707'),
  partition p08 values in ('201708'),
  partition p09 values in ('201709'),
  partition p10 values in ('201710'),
  partition p11 values in ('201711'),
  partition p12 values in ('201712'),
  partition p13 values in ('201801'),
  partition p14 values in ('201802'),
  partition p15 values in ('201803'),
  partition p16 values in ('201804'),
  partition p17 values in ('201805'),
  partition p18 values in ('201806'),
  partition p19 values in ('201807'),
  partition p20 values in ('201808'),
  partition p21 values in ('201809'),
  partition p22 values in ('201810'),
  partition p23 values in ('201811'),
  partition p24 values in ('201812')
  )

create table price_jd(              #京东商品价格表
  id int auto_increment primary key, #自增主键
  crawl_id char(6) not null,        #抓取编号
  sku varchar(45),                 #sku_jd.sku_group
  sku_name varchar(200),            #sku名称
  sku_price varchar(15),           #sku价格
  stock_state varchar(50),          #库存状态
  shop_id varchar(45),              #店铺编号
  shop_name varchar(45),            #店铺名称
  shop_score varchar(15),          #店铺评分
  follow_count varchar(15),                 #店铺关注人数
  vender_type varchar(6),           
  ware_type varchar(6),           
  diamond varchar(10),
  ware_score varchar(15),          #商品评分
  avg_ware_score varchar(15),      
  ware_score_level varchar(6),      #商品评分级别
  efficiency_score varchar(15),    #物流评分
  avg_efficiency_score varchar(15),      
  efficiency_score_level varchar(6), #物流评分级别  
  service_score varchar(15),       #服务评分
  avg_service_score varchar(15),      
  service_score_level varchar(6),   #服务评分级别  
  service_provider varchar(100),    #由***发货，由**提供售后服务
  ware_provider varchar(15),        #自营
  crawl_date varchar(45),
  crawl_time varchar(45)) engine=InnoDB;  
  
create table comment_jd(
  id int auto_increment primary key, #自增主键
  category_level3_id varchar(20),   #category_jd.category_level3_id
  brand_id varchar(15),             #category_jd.brand_id
  sku_group varchar(20),            #sku_jd.sku_group  
  max_page int,                     #该sku_group评论的页数,smallint小了
  page_index int,                   #当前评论所在的页数
  image_list_count smallint,        #sku_group评论中图片总数
  comment_id bigint,                #评论id
  content text,                     #评论内容
  creation_time char(19),           #评论创建时间
  reference_time char(19),          #基准时间，顾客收货时间
  reference_id varchar(20),         #基准sku，最精确的sku
  reference_name varchar(200),      #sku_group名称，不是基准sku名称
  reply_count smallint,             #评论回复数量
  score tinyint,                    #评分            
  useful_vote_count smallint,       #该评论的点赞数量
  user_image_url varchar(200),      #用户头像url
  user_level_id varchar(10),        #用户级别
  user_province varchar(20),        #省份
  user_register_time char(19),      #注册时间
  nickname varchar(45),             #用户名
  product_color varchar(45),        #产品颜色
  product_size varchar(45),         #产品尺寸
  image_count tinyint,              #该评论的图片数量
  anonymous_flag tinyint,           #匿名标志 1匿名 0未匿名 2未知
  user_level_name varchar(45),      #会员级别
  user_client_show varchar(45),     #设备来源，安卓...
  is_mobile tinyint,                #是否移动端，1是，0否，2未知
  days smallint,                    #收货多少天后评论
  crawl_date char(10),              #爬取日期
  crawl_time char(8),                #爬取时间
  index(category_level3_id),
  index(brand_id),
  index(sku_group)
) engine=InnoDB;

create table comment_jd_score_1 like comment_jd; #1分评论内容

create table proxy(
  id int auto_increment primary key, #自增主键
  ip varchar(15) not null,           #ip
  port varchar(10),                  #port
  protocol varchar(5),               #http or https
  url varchar(100),                  #爬取的网址
  crawl_date varchar(45),            #爬取日期
  crawl_time varchar(45)             #爬取时间
) engine=InnoDB;

create table price_history_jd(
  id int auto_increment primary key, #自增主键
  crawl_id char(6) not null,        #抓取编号 
  category_level3_id varchar(20),   #category_jd.category_level3_id
  brand_id varchar(15),             #category_jd.brand_id
  sku_group varchar(20),            #sku_jd.sku_group  
  date_begin date,                  #该价格开始时间
  date_end date,                    #该价格结束时间
  price decimal(10, 2),             #价格
  crawl_date date,                  #爬取日期
  crawl_time time,                  #爬取时间
  index(crawl_id),
  index(category_level3_id),
  index(brand_id),
  index(sku_group),
  index(date_begin)
) engine=InnoDB;


create table shop_jd(
  id int auto_increment primary key, #自增主键
  crawl_id char(6) not null,        #抓取编号
  shop_id varchar(15),              #店铺编码
  shop_name varchar(100),           #店铺名称
  is_zy tinyint,                    #是否自营，1是，0否
  location varchar(15),             #所在地
  total_score float,                #店铺综合评分
  total_score_percent float,        #综合评分与同行业平均水平相比的差距
  ware_score float,                 #商品质量得分
  ware_score_percent float,         #商品质量得分与同行业平均水平相比的差距
  service_score float,              #服务得分
  service_score_percent float,      #服务得分与同行业平均水平相比的差距
  logistics_score float,            #物流得分
  logistics_score_percent float,    #物流得分与同行业平均水平相比的差距
  description_score float,          #商品描述得分
  description_score_percent float,  #商品描述得分与同行业平均水平相比的差距
  return_score float,               #退换货处理得分
  return_score_percent float,       #退换货处理得分与同行业平均水平相比的差距
  return_duration float,            #售后处理时长，售后处理时长=审核时长+退换货处理时长
  return_duration_avg float,        #行业平均售后处理时长
  dispute_ratio float,              #交易纠纷率
  dispute_ratio_avg float,          #行业平均交易纠纷率
  repair_ratio float,               #退换货返修率
  rapair_ratio_avg float,           #行业平均退换货返修率
  illegal_times smallint,           #该店违法违规次数
  crawl_date date,                  #爬取日期
  crawl_time time,                  #爬取时间
  index(crawl_id),
  index(shop_id)
) engine=InnoDB;
  
  
  
  
