from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'client.views.home', name='home'),
    url(r'^client/$', 'client.views.index',name="admin"),
    url(r'^client/list_spiders/$','client.views.list_spiders',name='list_spiders'),
    url(r'^client/list_new_spiders/$','client.views.list_new_spiders',name='list_new_spiders'),
    url(r'^client/add_spiders/$','client.views.add_spiders',name='add_spiders'),
    url(r'^client/new_crawl/$','client.views.new_crawl',name='new_crawl'),
    url(r'^client/interupt_crawl/$','client.views.interupt_crawl',name='interupt_crawl'),
    url(r'^client/resume_crawl/$','client.views.resume_crawl',name='resume_crawl'),
    url(r'^client/list_status/$','client.views.list_status',name='list_status'),
    url(r'^client/list_requests/$','client.views.list_requests',name='list_status'),
    url(r'^client/list_instance/$','client.views.list_instance',name='list_instance'),
    url(r'^client/list_instance_status/$','client.views.list_instance_status',name='list_instance_status'),
    url(r'^client/list_pages_crawled/$','client.views.list_pages_crawled',name='list_pages_crawled'),
    url(r'^client/list_images_crawled/$','client.views.list_images_crawled',name='list_images_crawled'),
    url(r'^client/list_redis/$','client.views.list_redis',name='list_redis'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
