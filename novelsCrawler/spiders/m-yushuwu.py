#!/usr/bin/env python
# coding=utf-8
"""
Created on April 15 2017

@author: yytang
"""

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.spiders.novelSpider import NovelSpider


class YushuwuMobileSpider(NovelSpider):
    """
    classdocs

    examples:   https://m.yushuwu.com/novel/list/31271/1.html
                https://www.yushuwu.com/read/32570/
    """

    allowed_domains = ['m.yushuwu.com', 'www.yushuwu.com']
    name = get_spider_name_from_domain(allowed_domains[0])

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//title/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def url_check(self, url):
        pattern = 'https://www.yushuwu.com/read/([\d]+)'
        m = re.search(pattern, url)
        if m is not None:
            return 'https://m.yushuwu.com/novel/list/{0}/1.html/'.format(m.group(1))

        pattern1 = 'https://m.yushuwu.com/novel/([\d]+).html'
        m = re.search(pattern1, url)
        if m is not None:
            return 'https://m.yushuwu.com/novel/list/{0}/1.html/'.format(m.group(1))
        return url

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//ul/li/a')
        subtitle_selectors = subtitle_selectors[1:-1]

        def cmp(item):
            text = item.xpath('text()').extract()[0]
            p = '[^\d]+([\d]+)'
            return int(re.search(p, text).group(1))

        subtitle_selectors.sort(key=cmp)

        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            m = re.search("javascript:[t|g]oChapter\(([\d]+),([\d]+)\);", subtitle_url)
            if m is not None:
                subtitle_url = '/novel/{0}/{1}.html'.format(m.group(1), m.group(2))
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="nr1"]/text()').extract()
        content += sel.xpath('//div[@id="nr1"]/p/text()').extract()
        content = polish_content(content)
        return content

    def get_next_page_url(self, response):
        sel = Selector(response)
        next_page_url = sel.xpath('//div[@id="page"]/a[contains(text(), "下一页")]/@href').extract()[0]
        if "javascript" in next_page_url:
            return None
        else:
            return next_page_url
