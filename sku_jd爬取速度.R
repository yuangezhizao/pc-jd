###############################
#customer.sku_jd爬取速度
###############################

rm(list=ls(all=T));gc()
library(data.table)
library(RODBC)
library(ggplot2)

mysql<-odbcConnect('lz',uid='root',pwd='root',DBMSencoding='utf-8')
data<-data.table(sqlQuery(mysql,'select * from sku_jd'))
data[,hour:=substr(crawl_time,1,2)]
data[,time:=paste(crawl_date,hour,sep=' ')]
count<-data.table(table(data$time))



