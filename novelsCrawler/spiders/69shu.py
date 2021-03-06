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


class Six9shuSpider(NovelSpider):
    """
    classdocs

    example: http://www.69shu.com/28207/
    """

    allowed_domains = ['www.69shu.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    # custom_settings = {
    #     'DOWNLOAD_DELAY': 0.3,
    # }

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name, useless_ending='最新章节列表')
        return title

    def parse_episodes(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//div[@class="mu_contain"]')
        subtitle_selectors = subtitle_selectors[1].xpath('ul[@class="mulu_list"]/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@class="yd_text2"]/text()').extract()
        content = polish_content(content)
        return content
