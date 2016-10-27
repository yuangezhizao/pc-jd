#################
#导出数据库中的表
#按抓取编号导出,每次导出一个抓取编号

#################

rm(list=ls(all=T));gc()
library(data.table)
library(RODBC)

output <- function(crawl_id, table_name)
{
mysql <- odbcConnect('lz-home', uid='commen', pwd='1111', DBMSencoding='gbk')
sql <- paste('select * from ', table_name, ' where crawl_id=', crawl_id, sep='')
data <- data.table(sqlQuery(mysql, sql))
path <- paste('f:/customer/', table_name, '_', crawl_id, '.csv', sep='')
write.csv(data, path, row.names=F)
odbcCloseAll()
}
