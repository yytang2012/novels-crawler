# -*- coding: utf-8 -*-

import abc

import pymongo
import scrapy
from pymongo import MongoClient
from scrapy.conf import settings

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem


class SimpleSpider(scrapy.Spider):
    """
    classdocs

    example: https://m.yushuwu.com/novel/31960.html
    """

    dom = 'm.simple.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    @abc.abstractmethod
    def parse_title(self, response):
        return ''

    @abc.abstractmethod
    def parse_subtitle_contents(self, response):
        return []

    @abc.abstractmethod
    def get_next_page_url(self, response):
        return []

    @abc.abstractmethod
    def get_pages_url(self, response):
        return []

    def __init__(self, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)
        self.downloads_dir = kwargs['downloads_dir']
        # self.tmp_novels_dir = kwargs['tmp_novels_dir']
        urls = kwargs['start_urls']

        client = MongoClient(settings['MONGODB_URI'])
        self.db = client["Novels"]
        self.index = self.db['index']
        self.novel_dict = {}
        self.start_urls = self.preprocess_urls(urls)
        print(self.start_urls)

    def url_check(self, url):
        # pattern = 'http://m.lwxs.com/wapbook/([\d]+).html'
        # m = re.search(pattern, url)
        # if m is not None:
        #     return 'http://m.lwxs.com/wapbook/{0}_1/'.format(m.group(1))
        return url

    def preprocess_urls(self, urls):
        novel_info = self.db["novel_info"]
        new_urls = []
        for url in urls:
            new_url = self.url_check(url)
            novel = novel_info.find_one({'url': new_url})
            if not novel:
                new_urls.append(new_url)
            elif not os.path.isfile(novel['path']):
                novel_info.delete_one({'url': new_url})
                new_urls.append(new_url)

        return new_urls

    def parse(self, response):
        title = self.parse_title(response=response)

        index = self.index
        index.delete_many({'title': title})
        pages_url = self.get_pages_url(response)
        all_pages = [i for i in range(len(pages_url))]
        novel_index = {'title': title, 'url': response.url, 'pages': all_pages}
        index.insert_one(novel_index)

        self.novel_dict[title] = self.db[title]
        novel = self.novel_dict[title]
        for idx, subtitle_url in enumerate(pages_url):
            page_id = idx
            page_info = novel.find_one({'page_id': page_id})
            if not page_info:
                novel.insert_one(
                    {'title': title, 'page_id': page_id, 'content': None, 'subtitle_url': subtitle_url})

        for page in novel.find().sort('page_id', pymongo.ASCENDING):
            if not page['content'] and page['subtitle_url']:
                item = NovelsCrawlerItem()
                item['id'] = page['page_id']
                item['title'] = title
                print(page['subtitle_url'])
                request = scrapy.Request(page['subtitle_url'], callback=self.parse_page)
                request.meta['item'] = item
                yield request

    def parse_page(self, response):
        item = response.meta['item']
        page_id = item['id']
        title = item['title']
        novel = self.novel_dict[title]

        subtitle, contents = self.parse_subtitle_contents(response)
        item['subtitle'] = subtitle
        item['content'] = contents

        next_page_url = self.get_next_page_url(response)
        if next_page_url:
            next_page_id = page_id + 1
            next_page = novel.find_one({'page_id': next_page_id})
            if next_page and next_page['subtitle_url']:
                pass
            else:
                next_page['subtitle_url'] = next_page_url
                novel.find_one_and_update({'page_id': next_page_id}, {"$set": next_page}, upsert=True)
                new_item = NovelsCrawlerItem()
                new_item['id'] = next_page['page_id']
                new_item['title'] = title
                request = scrapy.Request(next_page['subtitle_url'], callback=self.parse_page)
                request.meta['item'] = new_item
                yield request

        yield item
