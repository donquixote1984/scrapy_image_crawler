# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import urlparse
import os
import os.path
from cStringIO import StringIO
from scrapy.http import Request
from scrapy import log
from tugouspider.storage.fs import FSFilesStore
from tugouspider.storage.scheme import STORE_SCHEMES

class ContentPipeline(object):
    def __init__(self,store_uri):
        self.store_uri = store_uri
        self.store = self._get_store(store_uri)
        pass
    def process_item(self, item, spider):
    	if item["page"] == None:
            print "dup"
            return item
        if not item["page"].has_key("crawled"):
            return item
    	if item["page"]["crawled"]==None:
            print "dup"
            return item
    	if item["page"]["crawled"]==True:
            print "dup"
            return item
        info  = spider.name
    	page_id  = item["page"]["id"]
    	page_url = item["page"]["url"]
    	if page_id == None or page_url ==None:
    		return item
    	basedir = page_id
    	basedir_meta = basedir+"/meta_key"
    	meta_data = item["page"]["meta_key"]
    	self.store.persist_text(basedir_meta,meta_data,info)

        basedir_meta = basedir+"/meta_description"
        meta_data = item["page"]["meta_description"]
        self.store.persist_text(basedir_meta,meta_data,info)

    	basedir_title = basedir+"/title"
        title_data = item["page"]["title"]
        self.store.persist_text(basedir_title,title_data,info)

    	basedir_content = basedir+"/content"
        content_data = item["page"]["body"]
        self.store.persist_text(basedir_content,content_data,info)

    	basedir_url = basedir+"/url"
        url_data = item["page"]["url"]
        self.store.persist_text(basedir_url,url_data,info)
        return item

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings.get("CONTENT_STORE")
        return cls(store_uri)

    def _get_store(self,uri):
    	if os.path.isabs(uri):
            scheme = 'file'
        else:
            scheme = urlparse.urlparse(uri).scheme
        store_cls = STORE_SCHEMES[scheme]
        return store_cls(uri)