#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider, re


class ShenshuwSpider(NovelSpider):
    """
    classdocs

    example: http://www.shenshuw.com/s34805/, http://m.shenshuw.com/34/34805/
    """

    allowed_domains = ['www.shenshuw.com', 'm.shenshuw.com']
    name = get_spider_name_from_domain(allowed_domains[0])

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def url_check(self, url):
        pattern = 'http://m.shenshuw.com/[\d]+/([\d]+)'
        m = re.search(pattern, url)
        if m is not None:
            return 'http://www.shenshuw.com/s{novel_id}/'.format(novel_id=m.group(1))
        return url

    def parse_episodes(self, response):
        sel = Selector(response)
        episodes = []
        subtitle_selectors = sel.xpath('//ul[@id="chapterlist"]/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episodes.append((page_id, subtitle_name, subtitle_url))
        return episodes

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="book_text"]/text()').extract()
        content = polish_content(content)
        return content
