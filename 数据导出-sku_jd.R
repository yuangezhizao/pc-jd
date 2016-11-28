#################
#导出数据库中的表
#按抓取编号导出,每次导出一个抓取编号

#################

rm(list=ls(all=T));gc()
library(data.table)
library(RODBC)

output <- function(sql, file_name)
{
mysql <- odbcConnect('customer', uid='root', pwd='1111', DBMSencoding='utf8')
data <- data.table(sqlQuery(mysql, sql))
path <- paste('f:/customer/', file_name, '.csv', sep='')
write.csv(data, path, row.names=F)
odbcCloseAll()
}
output('select * from comment_jd where concat(first_category, ",", second_category, ",", third_category)=
       "9987,653,655"', 'comments_9987-653-655')
output('select * from comment_jd where concat(first_category, ",", second_category, ",", third_category)=
       "9192,9196,1502"', 'comments_9192-9196-1502')
output('select * from comment_jd where concat(first_category, ",", second_category, ",", third_category)=
       "737,794,870"', 'comments_737-794-870')
output('select * from comment_jd where concat(first_category, ",", second_category, ",", third_category)=
       "737,794,798"', 'comments_737-794-798')
output('select * from comment_jd where concat(first_category, ",", second_category, ",", third_category)=
       "737,13297,1300"', 'comments_737-13297-1300')

