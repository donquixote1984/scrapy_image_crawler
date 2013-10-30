import hashlib
import redis
import copy
from scrapy.http import Request
from scrapy import log
from scrapy.contrib.pipeline.images import ImageException

class CachePipeline(object):
    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        server = redis.Redis(host, port)
        image_set = settings.get('REDIS_IMAGE_SET','images')
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        return cls(server,image_set)

    def __init__(self,server,image_set):
        self.server=server
        self.image_set=image_set

    def process_item(self, item, spider):
        key = "%s:%s"%(spider.name,self.image_set)
        urls = item["image_urls"]
        if urls ==None:
            return item
        if len(urls) <1:
            return item
        _urls  = copy.deepcopy(urls)
        for url in _urls:
            if url == None or url =="":
                continue
            hash_url = hashlib.sha1(url).hexdigest()   
            if self.server.sismember(key,hash_url):
                urls.remove(url)
                log.msg("duplicate image url: %s"%(url),level=log.WARNING)
            else:
                self.server.sadd(key,hash_url)
        return item
