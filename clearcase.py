import os
import MySQLdb
import redis
import datetime
import shutil
#clear log
os.remove("log/scrapy.log")
f=open("log/scrapy.log","a")
f.write("\n")
f.close()
#clear image
if os.path.exists("images/full"):
    shutil.rmtree("images/full")
if os.path.exists("pages"):
    shutil.rmtree("pages")
if os.path.exists("scrapy_downloads"):
    print "clear content"
    shutil.rmtree("scrapy_downloads")
#clear data
conn = MySQLdb.connect(host="localhost",user="root",passwd="passw0rd",db="tugou",charset="utf8")
cursor = conn.cursor()
time  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

sql="delete from images where id<>%s"
param =(time,)
cursor.execute(sql,param)

sql = "delete from pages where id <>%s"
param=(time,)
cursor.execute(sql,param)

#clear cache
r = redis.Redis(host='localhost', port=6379 )
info = r.info()
for key in r.keys():
    r.delete(key)
#kill scrapy
lines=os.popen("ps aux|grep scrapy")
for line in lines:
    vars1 = line.split()
    if line.find("grep scrapy")!=-1:
        continue
    if line.find("scrapyd")!=-1:
        continue
    pid=vars1[1]
    out = os.system("kill -9 "+pid)

#kill django client
lines = os.popen("ps aux|grep manage.py")
for line in lines:
    vars1= line.split()
    if line.find("grep manage.py")!=-1:
        continue
    pid=vars1[1]
    out = os.system("kill -9 "+pid)

print "clear all cases! ready for a new run."
