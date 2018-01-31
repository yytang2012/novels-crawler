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


class ExampleSpider(NovelSpider):
    """
    classdocs

    example: http://tw.zhsxs.com/zhschapter/43641.html
    """

    allowed_domains = ['tw.zhsxs.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
    }

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//tr/td[@class="chapterlist"]/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@style="font-size: 20px; line-height: 30px; word-wrap: break-word; table-layout: fixed; word-break: break-all; width: 700px; margin: 0 auto; text-indent: 2em; color: Black;"]/text()').extract()
        content = polish_content(content)
        return content
