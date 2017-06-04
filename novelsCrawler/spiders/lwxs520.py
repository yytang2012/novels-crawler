#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider


class Lwxs520Spider(NovelSpider):
    """
    classdocs

    example: http://www.lwxs520.com/books/33/33348/index.html
    """

    dom = 'www.lwxs520.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//div[@class="dccss"]/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//p/text()').extract()
        content = polish_content(content)
        return content
