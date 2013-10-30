import os
import urllib, json
from django.http import HttpResponse
from urlparse import urljoin
import redis
import MySQLdb
import endpoint
from django.core.paginator import Paginator
from django.shortcuts import render_to_response,RequestContext
from pages.models import Pages, Images
from django.core import serializers
from django.conf import settings
from scrapy.utils.reqser import request_from_dict
try:
    import cPickle as pickle
except ImportError:
    import pickle

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
PAGE_SIZE = 20 

rserver = redis.Redis(host=REDIS_HOST,port=REDIS_PORT)
velocity_vector = {}
SPIDERS =  settings.SPIDERS
MAX_INST = settings.MAX_INSTANCE

OPTS = {"host":settings.SCRAPY_HOST,"port":settings.SCRAPY_PORT,"project":settings.SCRAPY_PROJECT}
def index(request):
	test= "123"
	return render_to_response("index.html",{"test":test})

def add_spiders(request):
	name = request.GET.get("name")
	if name == None:
		return HttpResponse('invalid name')
	rserver.set("%s:status"%name,"")
	return HttpResponse('success')
	pass

def new_crawl(request):
	name = request.GET.get("name")
	if name==None:
		status = {"status":"Error","message":"invalid name"}
		return HttpResponse(status)
	spider_counter= 0
	jobs = endpoint.list_jobs(OPTS)
	running_jobs= jobs["running"]
	for job in running_jobs:
		job_in_spider = job["spider"]
		if job_in_spider==name:
			spider_counter+=1
	if spider_counter>=MAX_INST:
		status={"status":"Error","message":"maximum instances! can not fork any more!"}
		return HttpResponse(json.dumps(status))
	result =endpoint.new_crawl(name,OPTS)
	return HttpResponse(json.dumps(result))

def resume_crawl(request):
	id = request.GET.get("id")
	if id==None:
		status = {"status":"Error","message":"invalid id"}
		return HttpResponse(status)
	spider_name = find_spider_by_id(id)
	if spider_name == None:
		status = {"status":"Error","message":"invalid id"}
		return HttpResponse(status)		
	result = endpoint.resume_crawl(id, spider_name , OPTS)
	return HttpResponse(json.dumps(result))

def interupt_crawl(request):
	id = request.GET.get("id")
	if id==None:
		status = {"status":"Error","message":"invalid id"}
		return HttpResponse(json.dumps(status))
	result = endpoint.interupt_crawl(id,OPTS)
	if result["status"]=="ok":
		keys = rserver.keys()
		for key in keys:
			if (":status" in key ) and (id in key):
				pos = key.index(":status")
				spider_name = key[0:pos]
				status_key = "%s:status:%s:status"%(spider_name,id)
				rserver.set(status_key,"stopping")
				break
	return HttpResponse(json.dumps(result))


def list_spiders(request):
	spiders ={}
	result = endpoint.list_spider(OPTS)
	spider_names = result["spiders"]
	for spider_name in spider_names:
		spiders[spider_name]={}

	jobs = endpoint.list_jobs(OPTS)
	running_jobs= jobs["running"]
	pending_jobs= jobs["pending"]
	finished_jobs= jobs["finished"]
	for job in running_jobs:
		job_in_spider = job["spider"]
		job_id = job["id"]
		pid = job["pid"] if job.has_key("pid") else ""
		r_key = "%s:status:%s:latest"%(job_in_spider,job_id)
		status_key = "%s:status:%s:status"%(job_in_spider,job_id)
		status =rserver.hgetall(r_key)
		redis_status =rserver.get(status_key)
		if len(status)==0:
			status["status"]="pending"
		elif redis_status == "stopping":
			status["status"]="stopping"
		elif redis_status == "finished":
			status["status"] == "finished"
		else:
			status["status"]="running"
		status["pid"]=pid
		spiders[job_in_spider][job_id]=status

	for job in pending_jobs:
		job_in_spider = job["spider"]
		job_id = job["id"]
		pid = job["pid"] if job.has_key("pid") else ""
		r_key = "%s:status:%s:latest"%(job_in_spider,job_id)
		status =rserver.hgetall(r_key)
		status["status"]="pending"
		status["pid"]=pid
		spiders[job_in_spider][job_id]=status

	for job in finished_jobs:
		job_in_spider = job["spider"]
		job_id = job["id"]
		pid = job["pid"] if job.has_key("pid") else ""
		r_key = "%s:status:%s:latest"%(job_in_spider,job_id)
		status_key = "%s:status:%s:status"%(job_in_spider,job_id)
		redis_status = rserver.get(status_key)
		#if redis_status != "finished":
		#	rserver.set(status_key, "finished")
		status =rserver.hgetall(r_key)
		if len(status)==0:
			status["status"]="pending"
		else:
			status["status"]="finished"
		status["pid"]=pid
		spiders[job_in_spider][job_id]=status

	return HttpResponse(json.dumps(spiders))
"""
def list_spiders(request):
	keys = rserver.keys()	
	spiders = {}
	for key in keys: 
		if ":status" in key:
			#content= rserver.hgetall(key)
			#if content["instance_id"] == None :
			#	continue
			hash = {}
			#it is a spider instance
			pos = key.index(":status")
			spider_name = key[0:pos]
			if spiders.has_key(spider_name):
				if ":latest" in key:
					print key
					content = rserver.hgetall(key)
					if content["instance_id"] !=None:
						spiders[spider_name][content["instance_id"]]=content
			else:
				instance_list = {}
				spiders[spider_name] = instance_list
				if ":latest" in key:
					print key
					content = rserver.hgetall(key)
					if content["instance_id"] !=None:
						spiders[spider_name][content["instance_id"]]=content
			#instance_list = {}
			#instance_list[content["instance_id"]] = content
			#spiders[spider_name]=instance_list
	return HttpResponse(json.dumps(spiders))
"""
def list_status(request):
    keys = rserver.keys()
    instance_list = []
    for key in keys:
    		if ":latest" in key:
    			content = json.loads(rserver.hgetall(key))
    			instance_list.append(content)
    return HttpResponse(json.dumps(instance_list))

def list_instance(request):
	key = request.GET.get("key")
	if not "latest" in key:
		return HttpResponse("Invalid param")
	status = rserver.hgetall(key)
	if status == None:
		return HttpResponse('Invalid Key!')
	return HttpResponse(json.dumps(status))

def list_instance_status(request):
	key = request.GET.get("key")
	size= request.GET.get("size")
	if size == None:
		size=20
	if not is_number(size):
		return HttpResponse("What da fuck!")
	size = int(size)
	if key == None:
		return HttpResponse("Invalid Param")
	if not ":status" in key:
		return HttpResponse("Invalid Key")
	status_list= rserver.zrange(key,-size,-1)
	status_arr = []
	for status in status_list:
		print status
		status_json = json.loads(status)
		status_arr.append(status_json)
	return HttpResponse(json.dumps(status_arr))


def list_requests(request):
	#zrange
	spider = request.GET.get('spider')
	if spider == None:
		return HttpResponse('Invalid spider')
	p = request.GET.get('p')
	if p==None:
		p=1
	if is_number(p) == False:
		return HttpResponse('Invalid Page value')
	p = int(p)

	if p < 1:
		return HttpResponse('What da fuck!')

	start = (p-1)*PAGE_SIZE
	end = start+PAGE_SIZE-1
	keys = rserver.keys()
	json_array = []
	for key in keys:
		if key == spider+":requests":
			#is one request q
			results = rserver.zrange(key,start,end)
			for result in results:
				json_object = {}
				result = decode_request(result)
				json_object["url"] = result.url
				json_array.append(json_object)
	return HttpResponse(json.dumps(json_array))

def list_pages_crawled(request):
	p = request.GET.get('p')
	if p==None:
		return HttpResponse('Empty Page param')
	if is_number(p) == False:
		return HttpResponse('Invalid Page value')
	p = int(p)

	if p < 1:
		return HttpResponse('What the fuck!')

	pages = Pages.objects.all()
	paginator = Paginator(pages,PAGE_SIZE)
	pages = paginator.page(p)
	result = serializers.serialize('json',pages, indent=2, use_natural_keys=True)
	return HttpResponse(result)

def list_images_crawled(request):
	p = request.GET.get('p')
	if p==None:
		return HttpResponse('Empty Page param')
	if is_number(p) == False:
		return HttpResponse('Invalid Page value')
	p = int(p)

	if p < 1:
		return HttpResponse('What the fuck!')
	page_id = request.GET.get('page')	
	if page_id == None:
		return HttpResponse('Empty Page id')
	page = Pages.objects.get(id=page_id)
	if page == None:
		return HttpResponse('Invalid id ')
	print page
	images = page.images_set.all() 
	paginator = Paginator(images,PAGE_SIZE)
	images = paginator.page(p)
	result = serializers.serialize('json',images, indent=2, use_natural_keys=True)
	return HttpResponse(result)

def json_get(host,port, path):
    url = get_wsurl(host,port, path)
    return json.loads(urllib.urlopen(url).read())

def get_wsurl(host,port, path):
    return urljoin("http://%s:%s/"% (host, port), path)

def is_number(str):
	try:
		x = int(str)
	except ValueError:
		return False	

	return True

def decode_request(data):
    """Decode an request previously encoded"""
    return request_from_dict(pickle.loads(data))
    #return request_from_dict(pickle.loads(encoded_request))


def find_spider_by_id(id):
	keys = rserver.keys()
	for key in keys:
		if id in key:
			pos = key.index(":")			
			return key[0:pos]
	return None