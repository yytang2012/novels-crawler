# -*- coding: utf-8 -*-

import abc
import scrapy

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem


class NovelSpider(scrapy.Spider):
    """
    classdocs

    example: http://m.lwxs.com/wapbook/44108_1/
    """

    dom = 'www.example.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    @abc.abstractmethod
    def parse_title(self, response):
        return ''

    @abc.abstractmethod
    def parse_episoders(self, response):
        return []

    @abc.abstractmethod
    def parse_content(self, response):
        return []

    def __init__(self, *args, **kwargs):
        super(NovelSpider, self).__init__(*args, **kwargs)
        self.tmp_novels_dir = kwargs['tmp_novels_dir']
        urls = kwargs['start_urls']
        self.start_urls_dict = {}
        self.start_urls = [self.url_format(url) for url in urls]
        print(self.start_urls)

    def url_check(self, url):
        # pattern = 'http://m.lwxs.com/wapbook/([\d]+).html'
        # m = re.search(pattern, url)
        # if m is not None:
        #     return 'http://m.lwxs.com/wapbook/{0}_1/'.format(m.group(1))
        return url

    def url_format(self, url):
        new_url = self.url_check(url)
        self.start_urls_dict[new_url] = url
        return new_url

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield self.make_requests_from_url(url)

    def get_next_page_url(self, response):
        return None

    def parse(self, response):
        title_key = 'title'
        index_key = 'index'
        start_url_key = 'start_url'
        if start_url_key in response.meta:
            start_url = response.meta[start_url_key]
        else:
            start_url = response.url
        if index_key in response.meta:
            all_pages = response.meta[index_key]
        else:
            all_pages = []
        start_page = len(all_pages) + 1

        """ Get the title """
        if title_key in response.meta:
            title = response.meta[title_key]
        else:
            title = self.parse_title(response=response)

        """ Make sure a corresponding directory is created for the novel """
        tmp_spider_root_dir = os.path.join(self.tmp_novels_dir, title)
        if not os.path.isdir(tmp_spider_root_dir):
            os.makedirs(tmp_spider_root_dir)

        episoders = self.parse_episoders(response=response)
        existing_pages_list = existing_pages(tmp_spider_root_dir)
        for page_id, subtitle_name, subtitle_url in episoders:
            page_id += start_page
            all_pages.append(page_id)
            if page_id in existing_pages_list:
                continue
            else:
                item = NovelsCrawlerItem()
                item['title'] = title
                item['id'] = page_id
                item['subtitle'] = subtitle_name
                item['root_dir'] = tmp_spider_root_dir
                request = scrapy.Request(subtitle_url, callback=self.parse_page)
                request.meta['item'] = item
                yield request

        """ The following is useful only when multiple pages are downloaded """
        next_page_url = self.get_next_page_url(response=response)
        if next_page_url is not None:
            request = scrapy.Request(response.urljoin(next_page_url.strip()), callback=self.parse)
            request.meta[title_key] = title
            request.meta[index_key] = all_pages
            request.meta[start_url_key] = start_url
            yield request
        else:
            all_pages.sort()
            save_index(title, self.start_urls_dict[start_url], tmp_spider_root_dir, all_pages)

    def parse_page(self, response):
        item = response.meta['item']
        item['content'] = self.parse_content(response=response)
        return item
