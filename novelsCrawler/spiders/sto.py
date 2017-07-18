# -*- coding: utf-8 -*-

import scrapy
from scrapy import Selector

from libs.misc import get_spider_name_from_domain
from libs.polish import *
from novelsCrawler.items import NovelsCrawlerItem


class StoSpider(scrapy.Spider):
    """
    classdocs

    example: https://www.sto.cc/book-8976-1.html
    """

    dom = 'www.sto.cc'
    name = get_spider_name_from_domain(dom)
    allowed_domains = [dom]
    # tmp_root_dir = os.path.expanduser(settings['TMP_DIR'])

    def __init__(self, *args, **kwargs):
        super(StoSpider, self).__init__(*args, **kwargs)
        self.tmp_novels_dir = kwargs['tmp_novels_dir']
        urls = kwargs['start_urls']
        self.start_urls = [self.url_check(url) for url in urls]
        print(self.start_urls)

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield self.make_requests_from_url(url)

    def url_check(self, url):
        pattern = 'http://www.sto.cc/mbook-(\d+)-\d+.html'
        m = re.search(pattern, url)
        if m is not None:
            return 'http://www.sto.cc/{0}-1/'.format(m.group(1))
        return url

    def parse(self, response):
        sel = Selector(response)
        title = sel.xpath('//h1/text()').extract()[0]
        title = re.search(u'《([^》]+)》', title).group(1)
        title = polish_title(title, self.name)
        print(title)
        tmp_spider_root_dir = os.path.join(self.tmp_novels_dir, title)
        if not os.path.isdir(tmp_spider_root_dir):
            os.makedirs(tmp_spider_root_dir)

        # Get the last page number
        last_url = sel.xpath('//div[@id="webPage"]/a/@href').extract()[-1]
        max_page = int(re.search(r'(\d+).html', last_url).group(1))

        # Get the url prefix
        page_url_prefix = re.match(r'(.+)-\d+\.html', response.url).group(1)

        web_pages = []
        web_url = response.url
        web_items = []
        for i in range(1, max_page + 1):
            page_item = {}
            url = "%s-%d.html" % (page_url_prefix, i)
            page_item['url'] = url
            subtitle = ''
            page_item['subtitle'] = subtitle
            page_item['id'] = i
            page_item['title'] = title
            page_item['root_dir'] = tmp_spider_root_dir
            web_items.append(page_item)
            web_pages.append(i)
        web_pages.sort()
        save_index(title, web_url, tmp_spider_root_dir, web_pages)
        pages = polish_pages(tmp_spider_root_dir, web_pages)

        for page_item in web_items:
            i = page_item['id']
            if i in pages:
                url = page_item['url']
                request = scrapy.Request(url, callback=self.parse_page)
                item = NovelsCrawlerItem()
                item['title'] = page_item['title']
                item['subtitle'] = page_item['subtitle']
                item['id'] = page_item['id']
                item['root_dir'] = page_item['root_dir']
                request.meta['item'] = item
                yield request

    def parse_page(self, response):
        item = response.meta['item']
        sel = Selector(response)
        content = sel.xpath('//div[@id="BookContent"]/text()').extract()
        content = polish_content(content)
        item['content'] = content
        return item



