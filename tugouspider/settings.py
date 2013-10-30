# Scrapy settings for tugouspider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'tugouspider'
BOT_VERSION = ''


#CONCURRENT_ITEMS = 1000
#CONCURRENT_REQUESTS = 30
IMAGES_MIN_HEIGHT = 200
IMAGES_MIN_WIDTH = 200

COOKIES_ENABLED = False
DEPTH_LIMIT=5

SPIDER_MODULES = ['tugouspider.spiders']
NEWSPIDER_MODULE = 'tugouspider.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
ITEM_PIPELINES = ['tugouspider.pipelines.cache.CachePipeline',
                 'tugouspider.pipelines.image.CustomImagesPipeline',
                 'tugouspider.pipelines.db.DBPipeline',
                 'tugouspider.pipelines.content.ContentPipeline',
                 ]
IMAGES_STORE="./scrapy_downloads/images"
LOG_FILE="./log/scrapy.log"

SCHEDULER = "tugouspider.scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = False
SCHEDULER_QUEUE_CLASS = 'tugouspider.scrapy_redis.queue.SpiderPriorityQueue'

#QUEUE_SIZE_LIMIT=2000

REDIS_SERVER="127.0.0.1"
REDIS_PORT=6379

VELOCITY_REFRESH =10 
VELOCITY_RATE =10 
EXTENSIONS = {
    'tugouspider.extension.counter.SpiderVelocityCounter':800,
}

CACHE_STATUS_ENABLED = True
CACHE_DOWNLOAD_ENABLED = True
CONTENT_STORE="./scrapy_downloads/pages"
WEBSERVICE_ENABLED=False
#For caching the downloaded image and page- >preview.
