#!/usr/bin/env python
# coding=utf-8
"""
Created on  2016

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

    example: http://m.yushuwu.net/novel/list/35797/1.html
    """

    dom = 'www.example.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    tmpDirPath = settings['TMP_DIR']

    # def start_requests(self):
    #     print("start")
    #     urlPath = os.path.join(self.tmpDirPath, self.name);
    #     fd = open(urlPath, 'r')
    #     urls = fd.readlines()
    #     fd.close()
    #     for url in urls:
    #         url = url.strip('\n').strip()
    #         yield self.make_requests_from_url(url)

    def parse(self, response):
        start_page_key = 'startPage'
        title_key = 'title'
        index_key = 'index'
        if start_page_key in response.meta:
            start_page = response.meta[start_page_key]
        else:
            start_page = 1
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

        dd = sel.xpath('//ul[@class="chapter"]/li/a')
        chapterItems = []
        chapterIds = []
        webUrlNums = len(dd)
        for i in range(0, webUrlNums):
            chapterItem = {}
            d = dd[i]
            url = d.xpath('@href').extract()[0]
            url = response.urljoin(url.strip())
            chapterItem['url'] = url
            subtitle = d.xpath('text()').extract()[0]
            subtitle = polishSubtitle(subtitle)
            chapterItem['subtitle'] = subtitle
            chapterItem['id'] = i + start_page
            chapterItem['title'] = title
            chapterItem['type'] = 'novels'
            chapterItems.append(chapterItem)
            chapterIds.append(chapterItem['id'])
        chapterIds.sort()
        page_index = page_index + chapterIds
        newChapterIds = polishChapterIds(title, chapterIds)

        for chapterItem in chapterItems:
            i = chapterItem['id']
            if i in newChapterIds:
                url = chapterItem['url']
                request = scrapy.Request(url, callback=self.parse_page)
                item = NovelsItem()
                item['title'] = chapterItem['title']
                item['subtitle'] = chapterItem['subtitle']
                item['id'] = chapterItem['id']
                item['type'] = chapterItem['type']
                request.meta['item'] = item
                yield request

        """ The following is useful only when multiple pages are downloaded """
        aa = sel.xpath('//div[@class="page"]/a')
        nextPageUrl = ''
        for a in aa:
            text = a.xpath('text()').extract()[0]
            nextPageUrl = ''
            if text == '下一页'.decode('utf-8'):
                nextPageUrl = a.xpath('@href').extract()[0]
                nextPageUrl = response.urljoin(nextPageUrl.strip())
                print(nextPageUrl)
                break

        if nextPageUrl != '':
            request = scrapy.Request(nextPageUrl, callback=self.parse)
            request.meta[start_page_key] = webUrlNums + start_page
            request.meta[title_key] = title
            request.meta[index_key] = page_index
            yield request
        else:
            page_index.sort()
            saveIndex(title, response.url, page_index, True)

    def parse_page(self, response):
        item = response.meta['item']
        sel = Selector(response)
        content = sel.xpath('//div[@id="nr1"]/text()').extract()
        content = polishContent(content)
        item['content'] = content
        return item
