import os
import ConfigParser
import subprocess
import time
os.chdir("scrapyd")
os.system("sudo python setup.py build")
os.system("sudo python setup.py install")
os.chdir("../")
popen= subprocess.Popen("scrapyd")
time.sleep(3)
os.system("scrapyd-deploy tugouspider -p tugouspider")
popen.terminate()
cf = ConfigParser.ConfigParser()
cf.read("install.conf")
mysql_client = cf.get("db","MYSQL_CLIENT_PATH")
mysql_usr = cf.get("db","MYSQL_USER")
mysql_pass = cf.get("db","MYSQL_PASSWORD")
redis_home = cf.get("db","REDIS_HOME")
print "importing data..."
current_path= os.getcwd()
os.system("%smysql -u%s -p%s -e \"CREATE DATABASE  IF NOT EXISTS tugou\" "%(mysql_client,mysql_usr,mysql_pass))
print "loaded database"
os.system("%smysql -u%s -p%s tugou < %s/sql/tugou.sql"%(mysql_client,mysql_usr,mysql_pass,current_path))
print "import successfully!"
print """
To start the spider, take the steps:
*******************************************************************************************
1. start your local redis
2. change to the tugouspider/client folder and start the django project
3. start scrapyd  by typing "scrapyd"
4. browse to http://localhost:8000/client and start the spider by clicking the tail button in spider list, the page will be automaticly refresh the status
5. the images and page text will be store in your home folder "~/scrapy_downloads"
6. for the redis status, a "redis-commander" tool in github could be helpful to track it. the redis-commander needs nodejs
7. for the spider status, despite the console can shows details, you still can browse the default scrapyd console. http://localhost:6800 
8. for further issues, pls check the README
********************************************************************************************
"""
