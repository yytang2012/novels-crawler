# -*- coding: utf-8 -*-

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider


class Lewen6Spider(NovelSpider):
    """
    classdocs

    example: http://www.lewen6.com/1/1929/
    """

    dom = 'www.lewen6.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
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
        episoders = []
        subtitle_selectors = sel.xpath('//div[@class="panel-body"]/ul[@class="list-group list-charts"]/li/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episoders.append((page_id, subtitle_name, subtitle_url))
        return episoders

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@class="panel-body content-body content-ext"]/text()').extract()
        content = polish_content(content)
        return content
