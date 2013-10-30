#!/usr/bin/python
#-*-coding:utf-8-*-

import redis
import time

from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint


class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplication filter"""

    def __init__(self, settings,spidername):
        """Initialize duplication filter

        Parameters
        ----------
        server : Redis instance
        key : str
            Where to store fingerprints
        """
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        self.server = redis.Redis(host, port)
        self.key = "dupefilter:%s" % spidername
        self.signal = "%s:signal" % spidername

    @classmethod
    def from_settings(cls, settings):
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        return cls(server, settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        """
            use sismember judge whether fp is duplicate.
        """
        signal = self.server.get(self.signal)
        if signal == None:
            self.server.set(self.signal, 1)
        if signal =="0": #no new request in. just shut the fuck down slowly,slowly
            return True
        fp = request_fingerprint(request)
        if self.server.sismember(self.key,fp):
            return True
        self.server.sadd(self.key, fp)
        return False

    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
        self.clear()

    def clear(self):
        """Clears fingerprints data"""
        self.server.delete(self.key)
