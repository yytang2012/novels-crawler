# -*- coding: utf-8 -*-
from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider


class Novel101Spider(NovelSpider):
    """
    classdocs

    example: https://novel101.com/novels/06576839-16e5-4782-a645-8e9310e56f56
    """

    allowed_domains = ['novel101.com']
    name = get_spider_name_from_domain(allowed_domains[0])

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episoders(self, response):
        sel = Selector(response)
        episoders = []
        subtitle_selectors = sel.xpath('//div[@class="list-group"]/a[@class="list-group-item"]')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('h4/text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@class="body"]/p/text()').extract()
        content = polish_content(content)
        return content
