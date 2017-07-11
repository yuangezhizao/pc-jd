-- 京东品牌表
create table if not exists brand_jd(
  id                    serial       not null     primary key,
  crawl_id              char(8)      not null,
  category_level3_id    varchar(20)  not null,
  category_level3_name  varchar(45)  not null,
  category_level2_name  varchar(45)  not null,
  category_level1_name  varchar(45)  not null,
  brand_id              varchar(15), 
  brand_name            varchar(60),  
  crawl_time            timestamp
  );
comment on table  brand_jd                       is  '京东品牌表';
comment on column brand_jd.id                    is  '自增主键';
comment on column brand_jd.crawl_id              is  '爬取编号';
comment on column brand_jd.category_level3_id    is  '三级类别编码';
comment on column brand_jd.category_level3_name  is  '三级类别名称';
comment on column brand_jd.category_level2_name  is  '二级类别名称';
comment on column brand_jd.category_level1_name  is  '一级类别名称';
comment on column brand_jd.brand_id              is  '品牌编码';
comment on column brand_jd.brand_name            is  '品牌名称';
comment on column brand_jd.crawl_time            is  '爬取日期和时间';
create index if not exists crawl_id on brand_jd(crawl_id);
create index if not exists category_level3_id on brand_jd(category_level3_id);


-- 京东sku表
create table if not exists sku_jd(
 id                      serial        not null     primary key,
 crawl_id                char(8)       not null,
 category_level3_id      varchar(20)   not null,
 brand_id                varchar(15)   not null,
 sku_group               varchar(20)   not null,
 sku                     varchar(20)   not null,
 sku_name                varchar(200),
 vender_id               varchar(15),
 shop_id                 varchar(15),
 sku_specs               json,
 crawl_time              timestamp
 );
comment on table sku_jd                           is '京东sku表';
comment on column sku_jd.id                       is '自增主键';
comment on column sku_jd.crawl_id                 is '爬取编号';
comment on column sku_jd.category_level3_id       is '三级类别编码';
comment on column sku_jd.brand_id                 is '品牌编码';
comment on column sku_jd.sku_group                is 'sku组';
comment on column sku_jd.sku                      is 'sku';
comment on column sku_jd.sku_name                 is 'sku名称';
comment on column sku_jd.vender_id                is '供应商id';
comment on column sku_jd.shop_id                  is '店铺id';
comment on column sku_jd.sku_specs                is 'sku规格';
comment on column sku_jd.crawl_time               is '爬取日期和时间'
create index if not exists crawl_id_sku_jd on sku_jd(crawl_id);
create index if not exists category_level3_id_sku_jd on sku_jd(category_level3_id);
create index if not exists brand_id on sku_jd(brand_id);
create index if not exists sku_group on sku_jd(sku_group);

















