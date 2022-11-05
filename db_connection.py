#!/usr/bin/env python
# coding: utf-8

import sys
import pymysql

host='localhost'
# Default 값은 3306  (Port 번호는 변경될 수 있음)
port=int(3306)
user='root'
passwd='root'
database='test'
autocommit=False

# Instantiate Connection
try:
   conn = pymysql.connect(user=user, password=passwd, 
       host=host, port=port, database=database, autocommit=autocommit)
except pymysql.Error as e:
   print(f"Error connecting to MariaDB Platform: {e}")
   sys.exit(1)

# Instantiate Cursor
cur = conn.cursor()

# sql query 
sql_squery = "select * from testtable"

# exec sql query 
cur.execute(sql_squery)

# fetch qeury result
rows = cur.fetchall()
print (rows,'\n')

# commit 
conn.commit()

# Clean up
cur.close()
conn.close()