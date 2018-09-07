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


class StoSpider(NovelSpider):
    """
    classdocs

    example:
    https://www.sto.cc/book-8976-1.html
    https://www.sto.cc/mbook-87222-1.html
    """

    allowed_domains = ['www.sto.cc']
    name = get_spider_name_from_domain(allowed_domains[0])
    # custom_settings = {
    #     'DOWNLOAD_DELAY': 0.3,
    # }

    def url_check(self, url):
        pattern = 'https?://www.sto.cc/m?book-(\d+)-\d+.html'
        m = re.search(pattern, url)
        if m is not None:
            return 'https://www.sto.cc/book-{0}-1.html'.format(m.group(1))

        return url

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = re.search(u'《([^》]+)》', title).group(1)
        title = polish_title(title, self.name)
        return title

    def parse_episodes(self, response):
        sel = Selector(response)

        # Get the last page number
        last_url = sel.xpath('//div[@id="webPage"]/a/@href').extract()[-1]
        max_page = int(re.search(r'(\d+).html', last_url).group(1))

        # Get the url prefix
        page_url_prefix = re.match(r'(.+)-\d+\.html', response.url).group(1)

        episodes = []
        for page_id in range(max_page):
            subtitle_name = ''
            subtitle_url = '{prefix}-{page_id}.html'.format(prefix=page_url_prefix, page_id=page_id+1)
            episodes.append((page_id, subtitle_name, subtitle_url))
        return episodes

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="BookContent"]/text()').extract()
        content = polish_content(content)
        return content
