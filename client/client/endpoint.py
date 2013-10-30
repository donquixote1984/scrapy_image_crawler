import sys, optparse, urllib, json
from urlparse import urljoin


def list_spider(opts):
    project_name = opts["project"]
    result_json = json_get(opts,'listspiders.json?project=%s'%project_name)
    return result_json

def list_jobs(opts):
    project_name = opts["project"]
    result_json = json_get(opts,'listjobs.json?project=%s'%project_name)
    return result_json

def new_crawl(spider,opts):
    project_name=opts["project"]
    params = {"project":project_name,"spider":spider}
    result_json = json_post(opts,'schedule.json',params)
    return result_json

def resume_crawl(id,name,opts):
    project_name=opts["project"]
    params = {"project":project_name,"spider":name,"setting":"CONTINUE_ID=%s"%id,"job_id":id}   
    result_json = json_post(opts,'schedule.json',params)
    return result_json

def interupt_crawl(id,opts):
    project_name=opts["project"]
    params = {"project":project_name,"job":id}
    result_json = json_post(opts,'cancel.json',params)
    result_json = json_post(opts,'cancel.json',params)
    result_json = json_post(opts,'cancel.json',params)
    return result_json

def get_wsurl(opts, path):
    return urljoin("http://%s:%s/"% (opts["host"], opts["port"]), path)

def json_get(opts, path):
    url = get_wsurl(opts, path)
    return json.loads(urllib.urlopen(url).read())
def json_post(opts,path,params):
    url = get_wsurl(opts,path)
    data =urllib.urlencode(params)
    return json.loads(urllib.urlopen(url,data).read())

