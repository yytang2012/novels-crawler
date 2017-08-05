#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""
import re

from scrapy import Selector

from libs.misc import get_spider_name_from_domain, page_convert_from_zero
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider


class YushuwuSpider(NovelSpider):
    """
    classdocs

    example: https://www.yushuwu.com/read/40595/
    """

    allowed_domains = ['www.yushuwu.com']
    name = get_spider_name_from_domain(allowed_domains[0])

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//dd[@class="chapter_list"]/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            m = re.search('javascript:Chapter\(([\d]+),([\d]+)\);', subtitle_url)
            if m is not None:
                subtitle_url = '/read/{0}/{1}/'.format(m.group(2), m.group(1))

            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_convert_from_zero(page_id, 3), subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@style="line-height: 30px;padding: 10px 50px;word-wrap: break-word;"]/p/text()').extract()
        content = polish_content(content)
        return content
