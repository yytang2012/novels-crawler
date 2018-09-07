# -*- coding: utf-8 -*-

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import polish_title, polish_subtitle, polish_content
from novelsCrawler.spiders.novelSpider import NovelSpider


class LwxiaoshuoSpider(NovelSpider):
    """
    classdocs

    example: http://lwxiaoshuo.com/20/20684/index.html
    """

    allowed_domains = ['lwxiaoshuo.com']
    name = get_spider_name_from_domain(allowed_domains[0])

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        return title

    def parse_episodes(self, response):
        sel = Selector(response)
        episodes = []
        subtitle_selectors = sel.xpath('//td/div[@class="dccss"]/a')
        for page_id, subtitle_selector in enumerate(subtitle_selectors):
            subtitle_url = subtitle_selector.xpath('@href').extract()[0]
            subtitle_url = response.urljoin(subtitle_url.strip())
            subtitle_name = subtitle_selector.xpath('text()').extract()[0]
            subtitle_name = polish_subtitle(subtitle_name)
            episodes.append((page_id, subtitle_name, subtitle_url))
        return episodes

    def parse_content(self, response):
        sel = Selector(response)
        content = sel.xpath('//div[@id="content"]/p/text()').extract()
        content = polish_content(content)
        return content
