#################
#导出customer.sku_jd
#按抓取编号导出,每次导出一个抓取编号

#################

rm(list=ls(all=T));gc()
library(data.table)
library(RODBC)

crawl_id <- scan()
mysql <- odbcConnect('customer',uid='root',pwd='1111')
sql <- paste('select * from sku_jd where crawl_id=', crawl_id, sep='')
sku_jd <- data.table(sqlQuery(mysql, sql))
path <- paste('f:/customer/', 'sku_jd_', crawl_id, '.csv', sep='')
write.csv(sku_jd, path, row.names=F)
