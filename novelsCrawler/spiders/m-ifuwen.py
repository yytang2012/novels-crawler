# -*- coding: utf-8 -*-

from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.spiders.simpleSpider import SimpleSpider


class MifuwenSpider(SimpleSpider):
    """
    classdocs

    example: https://m.ifuwen.com/novel/30264.html
    """

    dom = 'm.ifuwen.com'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]

    def parse_title(self, response):
        sel = Selector(response)
        title = sel.xpath('//title/text()').extract()[0]
        title = title.split('_')[0]
        title = polish_title(title, self.name)
        print(title)
        return title

    def parse_subtitle_contents(self, response):
        sel = Selector(response)
        subtitle = sel.xpath('//h1/text()').extract()[0]
        subtitle = polish_subtitle(subtitle)

        contents = sel.xpath('//div[@id="nr1"]/p/text()').extract()
        contents = polish_content(contents)
        return subtitle, contents

    def url_check(self, url):
        # pattern = 'http://m.lwxs.com/wapbook/([\d]+).html'
        # m = re.search(pattern, url)
        # if m is not None:
        #     return 'http://m.lwxs.com/wapbook/{0}_1/'.format(m.group(1))
        return url

    def get_next_page_url(self, response):
        sel = Selector(response)
        tmp = sel.xpath('//div[@class="nr_page"]/table/tr')
        next_page_url = tmp.xpath('td[@class="next"]/a/@href').extract()[0]
        mulu = tmp.xpath('td[@class="mulu"]/a/@href').extract()[0]
        next_page_url = None if next_page_url == mulu else response.urljoin(next_page_url)
        return next_page_url

    def get_pages_url(self, response):
        sel = Selector(response)
        pages_info_sel = sel.xpath('//div[@class="lb_mulu chapterList"]/ul/li/a')
        last_page_id = int(pages_info_sel[-1].xpath('text()').extract()[0])
        pages_url = [None for i in range(last_page_id)]
        for page_info_sel in pages_info_sel:
            try:
                page_id = int(page_info_sel.xpath('text()').extract()[0])
                subtitle_url = page_info_sel.xpath('@href').extract()[0]
                subtitle_url = response.urljoin(subtitle_url)
                pages_url[page_id-1] = subtitle_url
            except Exception as e:
                pass
        return pages_url
