#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.spiders.novelSpider import NovelSpider


class YushuwuNetMobileSpider(NovelSpider):
    """
    classdocs

    example: http://m.yushuwu.net/novel/list/35797/1.html
    """


    allowed_domains = ['m.yushuwu.net']
    name = get_spider_name_from_domain(allowed_domains[0])
    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
    }

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//title/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//ul/li/a')
        subtitle_selectors = subtitle_selectors[1:-1]

        def cmp(item):
            text = item.xpath('text()').extract()[0]
            p = '[^\d]+([\d]+)'
            return int(re.search(p, text).group(1))

        subtitle_selectors.sort(key=cmp)
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            m = re.search("javascript:[t|g]oChapter\(([\d]+),([\d]+)\);", subtitle_url)
            if m is not None:
                subtitle_url = '/novel/{0}/{1}.html'.format(m.group(1), m.group(2))
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders


    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="nr1"]/text()').extract()
        content += sel.xpath('//div[@id="nr1"]/p/text()').extract()
        content = polish_content(content)
        return content

    def get_next_page_url(self, response):
        # if 'javascript' not in next_page_url:
        sel = Selector(response)
        next_page_url_list = sel.xpath('//div[@id="page"]/a[contains(text(), "下一页")]/@href').extract()
        if len(next_page_url_list) != 0:
            next_page_url = next_page_url_list[0]
            return next_page_url
        else:
            return None

#
# # -*- coding: utf-8 -*-
#
# import scrapy
# from scrapy import Selector
#
# from libs.misc import get_spider_name_from_domain
# from libs.polish import *
# from novelsCrawler.items import NovelsCrawlerItem
#
#
# class YushuwuNetMobileSpider(scrapy.Spider):
#     """
#     classdocs
#
#     example: http://m.yushuwu.net/novel/list/35797/1.html
#     """
#
#     dom = 'm.yushuwu.net'
#     name = get_spider_name_from_domain(dom)
#     allowed_domains = [dom]
#     custom_settings = {
#         'DOWNLOAD_DELAY': 0.2,
#     }
#
#     # tmp_root_dir = os.path.expanduser(settings['TMP_DIR'])
#
#     def __init__(self, *args, **kwargs):
#         super(YushuwuNetMobileSpider, self).__init__(*args, **kwargs)
#         self.start_urls = kwargs['start_urls']
#         self.tmp_novels_dir = kwargs['tmp_novels_dir']
#         print(self.start_urls)
#
#     # def start_requests(self):
#     #     for url in self.start_urls:
#     #         yield self.make_requests_from_url(url)
#
#     def parse(self, response):
#         start_page_key = 'startPage'
#         title_key = 'title'
#         index_key = 'index'
#         if start_page_key in response.meta:
#             start_page = response.meta[start_page_key]
#         else:
#             start_page = 1
#         if index_key in response.meta:
#             page_index = response.meta[index_key]
#         else:
#             page_index = []
#
#         sel = Selector(response)
#         if title_key in response.meta:
#             title = response.meta[title_key]
#         else:
#             title = sel.xpath('//title/text()').extract()[0]
#             title = polish_title(title, self.name)
#             print(title)
#
#         tmp_spider_root_dir = os.path.join(self.tmp_novels_dir, title)
#         if not os.path.isdir(tmp_spider_root_dir):
#             os.makedirs(tmp_spider_root_dir)
#
#         subtitle_selectors = sel.xpath('//ul/li/a')
#         subtitle_selectors = subtitle_selectors[1:-1]
#
#         def cmp(item):
#             text = item.xpath('text()').extract()[0]
#             p = '[^\d]+([\d]+)'
#             return int(re.search(p, text).group(1))
#
#         subtitle_selectors.sort(key=cmp)
#         all_pages = [i + start_page for i in range(0, len(subtitle_selectors))]
#         page_index += all_pages
#         download_pages = polish_pages(tmp_spider_root_dir, all_pages)
#
#         # Traverse the subtitle_selectors only crawler the pages that haven't been downloaded yet
#         for i, subtitle_selector in enumerate(subtitle_selectors):
#             page_id = i + start_page
#             if page_id not in set(download_pages):
#                 continue
#             else:
#                 subtitle_url = subtitle_selector.xpath('@href').extract()[0]
#                 m = re.search("javascript:[t|g]oChapter\(([\d]+),([\d]+)\);", subtitle_url)
#                 if m is not None:
#                     subtitle_url = '/novel/{0}/{1}.html'.format(m.group(1), m.group(2))
#                 subtitle_url = response.urljoin(subtitle_url.strip())
#                 subtitle_name = subtitle_selector.xpath('text()').extract()[0]
#                 subtitle_name = polish_subtitle(subtitle_name)
#
#                 item = NovelsCrawlerItem()
#                 item['title'] = title
#                 item['id'] = page_id
#                 item['subtitle'] = subtitle_name
#                 item['root_dir'] = tmp_spider_root_dir
#                 request = scrapy.Request(subtitle_url, callback=self.parse_page)
#                 request.meta['item'] = item
#                 yield request
#
#         """ The following is useful only when multiple pages are downloaded """
#         next_page_url = sel.xpath('//div[@id="page"]/a[contains(text(), "下一页")]/@href').extract()[0]
#         if 'javascript' not in next_page_url:
#             request = scrapy.Request(response.urljoin(next_page_url.strip()), callback=self.parse)
#             request.meta[start_page_key] = len(subtitle_selectors) + start_page
#             request.meta[title_key] = title
#             request.meta[index_key] = page_index
#             yield request
#         else:
#             save_index(title, response.url, tmp_spider_root_dir, page_index)
#
#     def parse_page(self, response):
#         item = response.meta['item']
#         sel = Selector(response)
#         content = sel.xpath('//div[@id="nr1"]/text()').extract()
#         content += sel.xpath('//div[@id="nr1"]/p/text()').extract()
#         content = polish_content(content)
#         item['content'] = content
#         return item
