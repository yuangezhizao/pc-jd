rm(list=ls(all=T));gc()
library(data.table)
library(RODBC)

mysql<-odbcConnect('lz',uid='root',pwd='1111',DBMSencoding='utf8')
sku_group<-data.table(sqlQuery(mysql,'select sku_group from sku_jd'))
sku_group<-unique(sku_group,by='sku_group')
sku_group_comment<-data.table(sqlQuery(mysql,'select sku_group from comment_count_jd'))
sku_group_comment<-unique(sku_group_comment,by='sku_group')
sku_group_comment[,flg:=1]
sku_group_no<-merge(sku_group,sku_group_comment,by='sku_group',all.x=T)
sku_group_no<-sku_group_no[is.na(flg)]
sku_group_no<-subset(sku_group_no,select=c(1))
sku_group_no[,sku_group:=as.character(sku_group)]
write.csv(sku_group_no,'C:/Users/Administrator/Documents/Temp/sku_group.csv',row.names=F)
#write.csv(sku_group,'C:/Users/Administrator/Documents/Temp/sku_group.csv',row.names=F)
