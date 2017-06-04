#!/usr/bin/env python
# coding=utf-8
"""
Created on June 4 2017

@author: yytang
"""

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.spiders.novelSpider import NovelSpider


class MlwxsSpider(NovelSpider):
    """
    classdocs

    example: http://m.lwxs.com/wapbook/44108_1/
    """

    dom = 'm.lwxs.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def url_check(self, url):
        pattern = 'http://m.lwxs.com/wapbook/([\d]+).html'
        m = re.search(pattern, url)
        if m is not None:
            new_url = 'http://m.lwxs.com/wapbook/{0}_1/'.format(m.group(1))
            return new_url
        else:
            return url

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h3/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//ul[@class="chapter"]/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="nr1"]/text()').extract()
        content = polish_content(content)
        return content

