import time
import datetime
import redis
import threading
import json
import copy
import signal
from scrapy import signals
from scrapy.exceptions import NotConfigured,CloseSpider

def h2j(o):
    if o == None:
        return o
    for key, value in o.items():
        if isinstance(value,datetime.datetime):
            value = value.strftime("%Y/%m/%d %H:%M:%S") 
        o[key] = value

    return o

def is_number(str):
    try:
        x = int(str)
    except ValueError:
        return False    
    return True

def hash_str2num(o):
    if o == None:
        return o
    hash = {}
    for key, value in o.items():
        if is_number(value):
            value = int(value)
        hash[key] = value
    return hash

class SpiderVelocityCounter(object):
    @classmethod
    def from_crawler(cls,crawler):
        settings = crawler.settings
        return cls(crawler,settings)

    def __init__(self,crawler,settings):
        self.settings = settings
        self.stats= crawler.stats
        redis_host = settings.get("REDIS_SERVER")
        redis_port= settings.get("REDIS_PORT")
        self.cache_history = settings.get("CACHE_STATUS_ENABLED")
        self.rserver = redis.Redis(host = redis_host,port=redis_port)
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        self.crawler= crawler

    def spider_opened(self,spider):
        if not hasattr(spider,"job_id"):
            spider.close_down=True
            raise CloseSpider(spider)
        if spider.job_id == None:
            spider.close_down=True
            raise CloseSpider(spider)
        if self.settings.get("CONTINUE_ID") == None:
            self.instance_id = spider.job_id
            self.stats.set_value('start_time', datetime.datetime.now(), spider=spider.name)
            self.stats.set_value("instance_id",self.instance_id,spider = spider.name)
            self.stats.set_value("status_time",datetime.datetime.now(),spider = spider.name)
        else:
            spider.job_id = self.settings.get("CONTINUE_ID")
            self.instance_id = spider.job_id
            rstat = self.rserver.hgetall("%s:status:%s:latest"%(spider.name,self.instance_id))
            if rstat==None or len(rstat)==0:
                spider.log("found no %s, start new spider." % self.instance_id)
                self.stats.set_value('start_time', datetime.datetime.now(), spider=spider.name)
                self.stats.set_value("instance_id",self.instance_id,spider = spider.name)
                self.stats.set_value("status_time",datetime.datetime.now(),spider = spider.name)
            else:
                #sync the stats
                if rstat.has_key("finish_time"):
                    del(rstat["finish_time"])
                if rstat.has_key("finish_reason"):
                    del(rstat["finish_reason"])
                self.stats.set_stats(rstat, spider=spider)

        status = spider.name +":status"
        status_id = status+":"+str(self.instance_id)
        status_list_id = status_id+":list"
        status_latest_id = status_id+":latest"
        status_instance_status = status_id+":status"
        self.rserver.set(status_instance_status,"running")
        #if self.cache_history:
        #    self.rserver.zadd(status_list_id,h2j(self.stats.get_stats(spider = spider.name)),int(time.time()*100))
        #self.rserver.hmset(status_latest_id,h2j(self.stats.get_stats(spider=spider.name)))
        self.thread = VeloStat(spider, self.settings, self.stats, self.rserver )
        self.thread.setDaemon(True)
        spider.log("open spider %s" % spider.name)
        spider.log("start monitoring velocity : %s " %spider.name)
        self.thread.start()        

    def spider_closed(self,spider):
        spider.log("close spider %s" % spider.name)
        self.stats.set_value('finish_time', datetime.datetime.now(), spider=spider.name)
        status = spider.name +":status"
        status_id = status+":"+str(self.instance_id)
        status_instance_status = status_id+":status"
        self.rserver.set(status_instance_status,"finished")
        if hasattr(self,"thread") and self.thread != None:
            self.thread.stop()

class VeloStat(threading.Thread):
    def __init__(self,spider,settings,stats,rserver):
        threading.Thread.__init__(self)
        self.spider = spider
        self.stats = stats
        self.rserver = rserver

        self.refresh_time = settings.get("VELOCITY_REFRESH")
        self.refresh_rate = settings.get("VELOCITY_RATE")
        self.thread_stop = False
        self.cache_history = settings.get("CACHE_STATUS_ENABLED")


    def run(self):
        while not self.thread_stop:
            time.sleep(self.refresh_rate)
            name = self.spider.name
            stats = copy.deepcopy(self.stats.get_stats(spider = name))
            if stats ==None:
                continue
            if not stats.has_key("instance_id"):
                continue
            if stats["instance_id"] == None:
                continue
            if not stats.has_key("scheduler/enqueued/redis"):
                continue
            if stats["scheduler/enqueued/redis"] == None:
                continue

            instance_id = stats["instance_id"]
            status_id = name+":status:"+str(instance_id)
            status_list_id = status_id+":list"
            status_latest_id = status_id+":latest"
            now = datetime.datetime.now()
            score = int(time.time()*100)
            stats["status_time"] = now
            if self.cache_history:
                self.rserver.zadd(status_list_id, json.dumps(h2j(stats)),score)
            self.rserver.hmset(status_latest_id,h2j(stats))
            

    def stop(self):
        self.thread_stop = True
        name = self.spider.name
        stats = self.stats.get_stats(spider = name)
        instance_id = stats["instance_id"]
        status_id = name+":status:"+str(instance_id)
        status_list_id = status_id+":list"
        status_latest_id = status_id+":latest"
        stats["status_time"]=datetime.datetime.now()
        stats["finish_time"]=datetime.datetime.now()
        if self.cache_history:
            self.rserver.zadd(status_list_id,json.dumps(h2j(stats)),int(time.time()*100))
        self.rserver.hmset(status_latest_id,h2j(stats))

