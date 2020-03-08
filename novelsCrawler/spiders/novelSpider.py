# -*- coding: utf-8 -*-

import abc
import scrapy

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem
from pymongo import MongoClient

from scrapy.utils.project import get_project_settings
settings = get_project_settings()



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
    def parse_episodes(self, response):
        return []

    @abc.abstractmethod
    def parse_content(self, response):
        return []

    def __init__(self, *args, **kwargs):
        super(NovelSpider, self).__init__(*args, **kwargs)
        self.downloads_dir = kwargs['downloads_dir']
        # self.tmp_novels_dir = kwargs['tmp_novels_dir']
        urls = kwargs['start_urls']

        client = MongoClient(settings['MONGODB_URI'])
        self.db = client["Novels"]

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
        start_page = len(all_pages)

        """ Get the title """
        if title_key in response.meta:
            title = response.meta[title_key]
        else:
            title = self.parse_title(response=response)

        # """ If the file exist in the downloads folder, no need to redo it """
        # if os.path.isfile(os.path.join(self.downloads_dir, title + '.txt')):
        #     return

        """ Make sure a corresponding directory is created for the novel """
        # tmp_spider_root_dir = os.path.join(self.tmp_novels_dir, title)
        # if not os.path.isdir(tmp_spider_root_dir):
        #     os.makedirs(tmp_spider_root_dir)

        episodes = self.parse_episodes(response=response)
        pages = self.db[title]
        # existing_pages_list = existing_pages(tmp_spider_root_dir)
        for page_id, subtitle_name, subtitle_url in episodes:
            page_id += start_page
            all_pages.append(page_id)
            if pages.find_one({'page_id': page_id}):
                continue
            else:
                item = NovelsCrawlerItem()
                item['title'] = title
                item['id'] = page_id
                item['subtitle'] = subtitle_name
                # item['root_dir'] = tmp_spider_root_dir
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
            index = self.db['index']
            index.delete_many({'title': title})
            novel_index = {'title': title, 'url': start_url, 'pages': all_pages}
            index.insert_one(novel_index)

    def parse_page(self, response):
        item = response.meta['item']
        item['content'] = self.parse_content(response=response)
        return item
