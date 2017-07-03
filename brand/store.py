# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 12:31:42 2017
存储
@author: Administrator
"""

import psycopg2
import sys
sys.path.append('C:/Users/Administrator/Documents/GitHub/pc-jd')
import config.db

def store(sql, records):
    conn = psycopg2.connect(host = config.db.host,
                            port = config.db.port,
                            user = config.db.user,
                            password = config.db.password,
                            database = config.db.database)
    cur = conn.cursor()
    for record in records:
        try:
            cur.execute(sql, record)
            conn.commit()
        except:
            print('error: store %s' % record)
            pass
    cur.close()
    conn.close()