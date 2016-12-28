# -*- coding: utf-8 -*-
import scrapy

from libs.misc import get_spider_name


class StoSpider(scrapy.Spider):
    dom = 'www.sto.cc'
    name = get_spider_name(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(StoSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs['start_urls']
        print(self.start_urls)

    def parse(self, response):
        pass
