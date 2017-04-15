#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""

import scrapy
from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem


class ExampleMobileSpider(scrapy.Spider):
    """
    classdocs

    example: http://m.daomengren.com/wapbook-7922/
    """

    dom = 'm.example.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def __init__(self, *args, **kwargs):
        super(ExampleMobileSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs['start_urls']
        self.tmp_novels_dir = kwargs['tmp_novels_dir']
        print(self.start_urls)

    def parse(self, response):
        start_page_key = 'startPage'
        title_key = 'title'
        index_key = 'index'
        original_url_key = 'original_url'
        if start_page_key in response.meta:
            start_page = response.meta[start_page_key]
            original_url = response.meta[original_url_key]
        else:
            start_page = 1
            original_url = response.url
        if index_key in response.meta:
            page_index = response.meta[index_key]
        else:
            page_index = []

        sel = Selector(response)
        if title_key in response.meta:
            title = response.meta[title_key]
        else:
            title = sel.xpath('//h3/text()').extract()[0]
            title = polish_title(title, self.name)
            print(title)
        tmp_spider_root_dir = os.path.join(self.tmp_novels_dir, title)
        if not os.path.isdir(tmp_spider_root_dir):
            os.makedirs(tmp_spider_root_dir)

        subtitle_selectors = sel.xpath('//ul[@class="chapter"]/li/a')
        all_pages = [i + start_page for i in range(0, len(subtitle_selectors))]
        page_index += all_pages
        download_pages = polish_pages(tmp_spider_root_dir, all_pages)

        """Traverse the subtitle_selectors only crawler the pages that haven't been downloaded yet"""
        for i, subtitle_selector in enumerate(subtitle_selectors):
            page_id = i + start_page
            if page_id not in set(download_pages):
                continue
            else:
                subtitle_url = subtitle_selector.xpath('@href').extract()[0]
                subtitle_url = response.urljoin(subtitle_url.strip())
                subtitle_name = subtitle_selector.xpath('text()').extract()[0]
                subtitle_name = polish_subtitle(subtitle_name)

                item = NovelsCrawlerItem()
                item['title'] = title
                item['id'] = page_id
                item['subtitle'] = subtitle_name
                item['root_dir'] = tmp_spider_root_dir
                request = scrapy.Request(subtitle_url, callback=self.parse_page)
                request.meta['item'] = item
                yield request

        """ The following is useful only when multiple pages are downloaded """
        next_page_url_list = sel.xpath('//div[@class="page"]/a[contains(text(), "下一页")]/@href').extract()
        if len(next_page_url_list) != 0:
            next_page_url = next_page_url_list[0]
            request = scrapy.Request(response.urljoin(next_page_url.strip()), callback=self.parse)
            request.meta[start_page_key] = len(subtitle_selectors) + start_page
            request.meta[title_key] = title
            request.meta[index_key] = page_index
            request.meta[original_url_key] = original_url
            yield request
        else:
            save_index(title, original_url, tmp_spider_root_dir, page_index)

    def parse_page(self, response):
        item = response.meta['item']
        sel = Selector(response)
        content = sel.xpath('//div[@id="nr1"]/text()').extract()
        content = polish_content(content)
        item['content'] = content
        return item
