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


class DaomengrenMobileSpider(NovelSpider):
    """
    classdocs

    example: http://m.daomengren.com/wapbook-7922/
    """

    dom = 'm.daomengren.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h3/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episodes(self, response):
        sel = Selector(response)
        episodes = []
        subtitle_selectors = sel.xpath('//ul[@class="chapter"]/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episodes.append((page_id, subtitle_name, subtitle_url))
        return episodes

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="nr1"]/text()').extract()
        content = polish_content(content)
        return content

    def get_next_page_url(self, response):
        sel = Selector(response)
        next_page_url_list = sel.xpath('//div[@class="page"]/a[contains(text(), "下一页")]/@href').extract()
        if len(next_page_url_list) != 0:
            next_page_url = next_page_url_list[0]
            return next_page_url
        else:
            return None
