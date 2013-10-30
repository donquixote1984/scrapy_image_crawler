#!/bin/sh
python client/manage.py runserver &
python client/manage.py runcrons &
scrapy crawl basic
