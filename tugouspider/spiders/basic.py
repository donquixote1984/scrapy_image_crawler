import re
import sys
import urllib2
import lxml.html
import lxml.etree
import uuid
import copy
import socket
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from tugouspider.items import TugouspiderItem
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http.request import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy import log
from tugouspider.rule.ban import BANURL,BANTOKEN
from scrapy.exceptions import CloseSpider
reload(sys)
sys.setdefaultencoding( "utf-8" )
socket.setdefaulttimeout (5)
IMG_TAG='img'
WEB_REGEX=r'^(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?$'

class BasicSpider(BaseSpider):
    name = 'basic'
    allowed_domains = ['huaban.com']
    start_urls = ['http://huaban.com']
    close_down = False
    job_id = None

    def __init__(self, name=None,_job=None, **kwargs):
        super(BasicSpider, self).__init__(name, **kwargs)
        self.r = re.compile(WEB_REGEX)
        self.crawl_content =True 
        self.job_id = _job if _job!=None else uuid.uuid1().hex

    def parse(self, response):
        if hasattr(self,"close_down") and self.close_down:
            raise CloseSpider(self)
        i=self.parse_image(response)
        links = self.parse_link(response) 
        if links!=None and len(links)!=0:
            for link in links:
                if not self.filter_link(link.url):
                    continue
                log.msg("start crawling new url : "+link.url, level=log.INFO)
                yield Request(link.url.strip(), self.parse)
        yield i

    def parse_link(self,response):
        """Basic link parser, extract all the link"""
        link_extractor = SgmlLinkExtractor()
        links = link_extractor.extract_links(response)
        return links

    def parse_image(self,response):
        hxs = HtmlXPathSelector(response)
        meta_key = ""
        meta_description=""
        title=""
        meta_key_node = hxs.select("//head/meta[translate(@name,'keywords','KEYWORDS')='KEYWORDS']/@content").extract()
        if len(meta_key_node)>0:
            meta_key = meta_key_node[0]
        meta_description_node =hxs.select("//head/meta[translate(@name,'description','DESCRIPTION')='DESCRIPTION']/@content").extract()
        if len(meta_description_node)>0:
            meta_description=meta_description_node[0]
        title_node = hxs.select("//head/title/text()").extract()
        if len(title_node)>0:
            title = title_node[0]
        body = ""
        if self.crawl_content:
            root = lxml.html.fromstring(response.body)
            lxml.etree.strip_elements(root,lxml.etree.Comment,"script","style","head","canvas","embed","object")
            body = lxml.html.tostring(root,method="text",encoding = unicode)
        images = hxs.select("//img[@src]")
        i = TugouspiderItem()
        i["page"] = {}
        _uuid = str(uuid.uuid1())
        i["page"]["id"] = _uuid
        i["page"]["url"]=response.url
        i["page"]["meta_key"] = meta_key
        i["page"]["meta_description"] = meta_description
        i["page"]["title"] = title
        i["page"]["body"] = body
        i["page"]["crawled"]=False
        i["image_urls"]=set()
        base_url = get_base_url(response)
        for image  in images:
            urls = image.select("@src").extract()
            if urls==None or len(urls)==0:
                return None
            url = image.select("@src").extract()[0]
            if url == None or url =="":
                continue
            url = self.relative_to_absolute_url(str(url),base_url)
            i["image_urls"].add(url)
        i["image_urls"]=list(i["image_urls"])
        return i 

    def is_url(self,url):
        if self.r.match(url):
            return True
        else:
            return False

    def relative_to_absolute_url(self,url,base_url):
        """/image/1.png to http://tugou.com/image/1.png"""
        if self.is_url(url):
            return url
        else:
            url= str(urljoin_rfc(base_url, url))
            self.test_url(url)
            return url

    def test_url(self,url):
        resp = urllib2.urlopen(url,timeout=3)
        if resp.getcode() != 200:
            log.msg("url test failure : "+url,level=log.WARNING)
            return False    
        else:
            return True

    def filter_link(self,link):
        if link in BANTOKEN:
            for token in BANTOKEN:
                if token in link:
                    return False
        if link in BANURL:
            return False
        return True  