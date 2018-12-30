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


class PiaotianSpider(NovelSpider):
    """
    classdocs

    example: https://www.piaotian.com/html/9/9459/index.html
    """

    allowed_domains = ['www.piaotian.com']
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
        episodes = []
        subtitle_selectors = sel.xpath('//div[@class="centent"]/ul/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episodes.append((page_id, subtitle_name, subtitle_url))
        return episodes

    def parse_content(self, response):
        # sel = Selector(response)
        # content = sel.xpath('//div[@id="content"]/p/text()').extract()
        # content = polish_content(content)
        html = str(response.body.decode('GBK'))
        pattern = r'&nbsp;&nbsp;&nbsp;&nbsp;(.*)'
        import re
        m = re.search(pattern, html)
        if m:
            content = m.group(1)
        else:
            content = ''
        content = content.replace('<br /><br />&nbsp;&nbsp;&nbsp;&nbsp;', '\n\n')
        return content
