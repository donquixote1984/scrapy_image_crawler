# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import os
import hashlib
import time
from cStringIO import StringIO
from urlparse import urlparse
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from PIL import Image
from scrapy.utils.misc import md5sum
from scrapy.http import Request
from scrapy import log

class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield Request(image_url)

    def image_key(self, url):
        o = urlparse(url)
        base_url=o.netloc
        if base_url==None and base_url=="":
            base_url="tugou.com"
        if ":" in base_url:
            base_urls = base_url.split(":")
            if len(base_urls)>0:
                base_url = base_urls[0]
            else:
                base_url="tugou.com"
        image_guid = hashlib.sha1(url).hexdigest()
        log.msg("image income : %s/%s.jpg"%(base_url,image_guid), level=log.INFO) 
        return 'full/%s/%s.jpg' % (base_url,image_guid)

    def image_downloaded(self, response, request, info):
        checksum = None
        for key, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            self.store.persist_image(key, image, buf, info)
            abs_path = self.store._get_filesystem_path(key)
            image_size = os.path.getsize(abs_path)
        width,height =image.size
        return {"checksum":checksum,"width":width, "height":height,"size":image_size}

    def media_downloaded(self, response, request, info):
        referer = request.headers.get('Referer')
        if response.status != 200:
            log.msg(format='Image (code: %(status)s): Error downloading image from %(request)s referred in <%(referer)s>',
                    level=log.WARNING, spider=info.spider,
                    status=response.status, request=request, referer=referer)
            raise ImageException('download-error')

        if not response.body:
            log.msg(format='Image (empty-content): Empty image from %(request)s referred in <%(referer)s>: no-content',
                    level=log.WARNING, spider=info.spider,
                    request=request, referer=referer)
            raise ImageException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        log.msg(format='Image (%(status)s): Downloaded image from %(request)s referred in <%(referer)s>',
                level=log.DEBUG, spider=info.spider,
                status=status, request=request, referer=referer)
        self.inc_stats(info.spider, status)

        try:
            key = self.image_key(request.url)
            result_hash = self.image_downloaded(response, request, info)
            checksum = result_hash["checksum"]
            width =result_hash["width"]
            height=result_hash["height"]
            size = result_hash["size"]
            self.inc_image_size(info.spider,size)
        except ImageException as exc:
            whyfmt = 'Image (error): Error processing image from %(request)s referred in <%(referer)s>: %(errormsg)s'
            log.msg(format=whyfmt, level=log.WARNING, spider=info.spider,
                    request=request, referer=referer, errormsg=str(exc))
            raise
        except Exception as exc:
            whyfmt = 'Image (unknown-error): Error processing image from %(request)s referred in <%(referer)s>'
            log.err(None, whyfmt % {'request': request, 'referer': referer}, spider=info.spider)
            raise ImageException(str(exc))

        return {'url': request.url, 'path': key, 'checksum': checksum,'width':width,'height':height,'size':size}

    def inc_image_size(self,spider,size):
        spider.crawler.stats.inc_value("image_downloaded_size",count=size,spider=spider)

    def get_images(self, response, request, info):
        key = self.image_key(request.url)
        orig_image = Image.open(StringIO(response.body))
        width, height = orig_image.size
        if width < self.MIN_WIDTH or height < self.MIN_HEIGHT:
            raise ImageException("Image too small (%dx%d < %dx%d)" %
                                 (width, height, self.MIN_WIDTH, self.MIN_HEIGHT))
        image, buf = self.convert_image(orig_image)
        yield key, image, buf

        for thumb_id, size in self.THUMBS.iteritems():
            thumb_key = self.thumb_key(request.url, thumb_id)
            thumb_image, thumb_buf = self.convert_image(image, size)
            yield thumb_key, thumb_image, thumb_buf