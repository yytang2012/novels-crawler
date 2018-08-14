# -*- coding: utf-8 -*-

import abc

import pymongo
import scrapy
from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem
from pymongo import MongoClient

from scrapy.conf import settings


class SimpleSpider(scrapy.Spider):
    """
    classdocs

    example: https://m.yushuwu.com/novel/31960.html
    """

    dom = 'm.yushuwu.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    # @abc.abstractmethod
    # def parse_title(self, response):
    #     return ''
    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//title/text()').extract()[0]
        title = title.split('_')[0]
        title = polish_title(title, 'yushuwu')
        print(title)
        return title

    @abc.abstractmethod
    def parse_episoders(self, response):
        return []

    @abc.abstractmethod
    def parse_content(self, response):
        return []

    def __init__(self, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)
        self.downloads_dir = kwargs['downloads_dir']
        # self.tmp_novels_dir = kwargs['tmp_novels_dir']
        urls = kwargs['start_urls']

        client = MongoClient(settings['MONGODB_URI'])
        self.db = client["Novels"]
        self.index = self.db['index']
        self.novel = None
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


    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield self.make_requests_from_url(url)

    def get_next_page_url(self, response):
        sel = Selector(response)
        tmp = sel.xpath('//div[@class="nr_page"]/table/tr')
        next_page_url = tmp.xpath('td[@class="next"]/a/@href').extract()[0]
        mulu = tmp.xpath('td[@class="mulu"]/a/@href').extract()[0]
        next_page_url = None if next_page_url == mulu else next_page_url
        return next_page_url

    def get_pages_url(self, response):
        sel = Selector(response)
        pages_info_sel = sel.xpath('//div[@class="lb_mulu chapterList"]/ul/li/a')
        last_page_id = int(pages_info_sel[-1].xpath('text()').extract()[0])
        pages_url = [None for i in range(last_page_id)]
        for page_info_sel in pages_info_sel:
            try:
                page_id = int(page_info_sel.xpath('text()').extract()[0])
                subtitle_url = page_info_sel.xpath('@href').extract()[0]
                pages_url[page_id-1] = subtitle_url
            except Exception as e:
                pass
        return pages_url

    def parse(self, response):
        title = self.parse_title(response=response)

        index = self.index
        index.delete_many({'title': title})
        pages_url = self.get_pages_url(response)
        all_pages = [i for i in range(len(pages_url))]
        novel_index = {'title': title, 'url': response.url, 'pages': all_pages}
        index.insert_one(novel_index)

        self.novel = self.db[title]
        for idx, subtitle_url in enumerate(pages_url):
            page_id = idx
            page_info = self.novel.find_one({'page_id': page_id})
            if not page_info:
                self.novel.insert_one({'title': title, 'page_id': page_id, 'content': None, 'subtitle_url': subtitle_url})

        for page in self.novel.find().sort('page_id', pymongo.ASCENDING):
            if not page['content'] and page['subtitle_url']:
                item = NovelsCrawlerItem()
                item['id'] = page['page_id']
                item['title'] = title
                # item['root_dir'] = tmp_spider_root_dir
                request = scrapy.Request(page['subtitle_url'], callback=self.parse_page)
                request.meta['item'] = item
                yield request

    def parse_page(self, response):
        item = response.meta['item']
        item['content'] = self.parse_content(response=response)
        page_id = item['id']
        title = item['title']

        sel = Selector(response)
        subtitle = sel.xpath('//h1/text()').extract()[0]
        item['subtitle'] = polish_subtitle(subtitle)

        contents = sel.xpath('//div[@id="nr1"]/p/text()').extract()
        item['content'] = polish_content(contents)

        next_page_url = self.get_next_page_url(response)
        if next_page_url:
            next_page_id = page_id + 1
            next_page = self.novel.find_one({'page_id': next_page_id})
            if next_page and next_page['subtitle_url']:
                pass
            else:
                next_page['subtitle_url'] = next_page_url
                self.novel.find_one_and_update({'page_id': next_page_id}, {"$set": next_page}, upsert=True)
                new_item = NovelsCrawlerItem()
                new_item['id'] = next_page['page_id']
                new_item['title'] = title
                # item['root_dir'] = tmp_spider_root_dir
                request = scrapy.Request(next_page['subtitle_url'], callback=self.parse_page)
                request.meta['item'] = new_item
                yield request

        yield item
