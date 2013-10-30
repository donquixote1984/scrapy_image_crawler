# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import datetime
import uuid
from scrapy.contrib.pipeline.images import ImagesPipeline
from twisted.enterprise import adbapi
import MySQLdb.cursors
from scrapy.http import Request
from scrapy import log

class DBPipeline(object):
    CACHE_DOWNLOAD = False
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', db='tugou',
                user='root', passwd='passw0rd', cursorclass=MySQLdb.cursors.DictCursor,
                charset='utf8', use_unicode=True)

    def process_item(self, item, spider):
        self.stats = spider.crawler.stats
        self.spider= spider
        self.insert_page(item)
        self.insert_image(item)
        return item

    @classmethod
    def from_settings(cls,settings):
        cls.CACHE_DOWNLOAD=settings.get("CACHE_DOWNLOAD_ENABLED",False)
        return cls()

    def insert_image(self, item):
        paths = item["images"]
        page_url = item["page"]["url"]
        if page_url == None:
            return 
        if paths==None:
            return
        for path in paths:
            result = self.dbpool.runInteraction(self._insert_image_callback,path,page_url)
            result.addErrback(self._insert_err)

    def insert_page(self, item):
        url = item["page"]["url"]
        if url == None:
            return
        result=self.dbpool.runInteraction(self._insert_page_callback,item)
        result.addErrback(self._insert_err)

    def _insert_image_callback(self,tx,path,page_url):
        now =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _uuid = str(uuid.uuid1())
        if page_url==None:
            return
        url = path["url"]
        fs_path = path["path"]
        width=path["width"] if path.has_key("width") else -1
        height=path["height"] if path.has_key("height") else -1
        size=path["size"] if path.has_key("size") else -1
        self.dbpool.runOperation("insert into images values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(_uuid,url,fs_path,page_url,now,now,str(width),str(height),str(size)))
        log.msg("persistant image : %s"%(path),level=log.INFO)
        if self.stats!=None and self.spider!=None: 
            self.stats.inc_value("db/image_saved_count",spider=self.spider)


    def _insert_page_callback(self,tx,item):
        page_url = item["page"]["url"]
        _uuid = item["page"]["id"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        page_url=item["page"]["url"]
        tx.execute("insert into pages values(%s,%s,%s,%s,%s)",(_uuid,page_url,now,now,''))
        log.msg("page inserted",level=log.INFO)
        if self.stats!=None and self.spider!=None:
            self.stats.inc_value("db/page_saved_count",spider=self.spider)

    def _insert_err(self,err):
        print err
        log.msg("DB ERROR: %s"%err, level=log.ERROR)