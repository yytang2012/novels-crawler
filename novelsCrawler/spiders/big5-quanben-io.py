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


class Big5QuanbenIOSpider(NovelSpider):
    """
    classdocs

    example: http://big5.quanben.io/n/yishouzhetian/list.html
    """

    allowed_domains = ['big5.quanben.io']
    name = get_spider_name_from_domain(allowed_domains[0])
    # custom_settings = {
    #     'DOWNLOAD_DELAY': 0.3,
    # }

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episodes(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//ul[@class="list3"]/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name_list = subtitle_selector.xpath('span/text()').extract()
            subtitle_name = subtitle_name_list[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="content"]/p/text()').extract()
        content = polish_content(content)
        return content
