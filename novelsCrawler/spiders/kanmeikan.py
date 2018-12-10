#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""
import re

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider


class KanmeikanSpider(NovelSpider):
    """
    classdocs

    example: http://book.kanmeikan.com/read/46398/
    """

    allowed_domains = ['book.kanmeikan.com']
    name = get_spider_name_from_domain(allowed_domains[0])
    custom_settings = {
        'DOWNLOAD_DELAY': 0.3,
    }

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episodes(self, response):
        sel = Selector(response)
        episodes = []
        subtitle_selectors = sel.xpath('//dl/dd[@class="chapter_list"]/a')
        episode_num = len(subtitle_selectors)
        for idx, subtitle_selector in enumerate(subtitle_selectors):
            if idx % 3 == 0:
                page_id = idx + 2
                if page_id >= episode_num:
                    page_id = episode_num - 1
            elif idx % 3 == 1:
                page_id = idx
                if page_id == episode_num - 1:
                    page_id -= 1
            else:
                page_id = idx - 2

            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            pattern = r'javascript:Chapter\((\d+),(\d+)\);'
            m = re.match(pattern, subtitle_url)
            if m:
                subtitle_url = '/read/{}/{}/'.format(m.group(2), m.group(1))
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episodes.append((page_id, subtitle_name, subtitle_url))
        return episodes

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@style="line-height: 30px;padding: 10px 50px;word-wrap: break-word;"]/p/text()').extract()
        content = polish_content(content)
        return content
