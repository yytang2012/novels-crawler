# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelsCrawlerItem(scrapy.Item):
    type = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    content = scrapy.Field()
    id = scrapy.Field()
    root_dir = scrapy.Field()