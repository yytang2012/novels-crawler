# -*- coding: utf-8 -*-

import scrapy
from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem


class BaishulouSpider(scrapy.Spider):
    """
    classdocs

    example: http://www.baishulou.net/read/48/48856/
    """

    dom = 'www.baishulou.net'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    handle_httpstatus_list = [521]

    # tmp_root_dir = os.path.expanduser(settings['TMP_DIR'])

    def __init__(self, *args, **kwargs):
        super(BaishulouSpider, self).__init__(*args, **kwargs)
        self.start_urls = kwargs['start_urls']
        self.tmp_novels_dir = kwargs['tmp_novels_dir']
        print(self.start_urls)

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield self.make_requests_from_url(url)

    def parse(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, self.name)
        print(title)
        tmp_spider_root_dir = os.path.join(self.tmp_novels_dir, title)
        if not os.path.isdir(tmp_spider_root_dir):
            os.makedirs(tmp_spider_root_dir)

        subtitle_selectors = sel.xpath('//td[@class="dccss"]/a')
        all_pages = [i+1 for i in range(0, len(subtitle_selectors))]
        save_index(title, response.url, tmp_spider_root_dir, all_pages)
        download_pages = polish_pages(tmp_spider_root_dir, all_pages)

        # Traverse the subtitle_selectors only crawler the pages that haven't been downloaded yet
        for i, subtitle_selector in enumerate(subtitle_selectors):
            page_id = i + 1
            if page_id not in set(download_pages):
                continue
            else:
                subtitle_url = subtitle_selector.xpath('@href').extract()[0]
                subtitle_url = response.urljoin(subtitle_url.strip())
                subtitle_name = subtitle_selector.xpath('text()').extract()[0]
                subtitle_name = polish_subtitle(subtitle_name)

                item = NovelsCrawlerItem()
                item['title'] = title
                item['id'] = page_id
                item['subtitle'] = subtitle_name
                item['root_dir'] = tmp_spider_root_dir
                request = scrapy.Request(subtitle_url, callback=self.parse_page)
                request.meta['item'] = item
                yield request

    def parse_page(self, response):
        item = response.meta['item']
        sel = Selector(response)
        content = sel.xpath('//div[@id="content"]/text()').extract()
        content = polish_content(content)
        item['content'] = content
        return item
