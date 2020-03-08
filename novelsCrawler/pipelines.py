# -*- coding: utf-8 -*-

from pymongo import MongoClient
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings
settings = get_project_settings()


class NovelsCrawlerPipeline(object):
    def __init__(self):
        MONGODB_URI = settings['MONGODB_URI']
        client = MongoClient(MONGODB_URI)
        self.db = client["Novels"]

    def process_item(self, item, spider):
        page_id = item['id']
        subtitle = item['subtitle']
        content = item['content']
        title = item['title']
        novel = self.db[title]

        # novel.insert_one({'title': title, 'page_id': page_id, 'content': content, 'subtitle': subtitle})
        novel.find_one_and_update({'page_id': page_id},
                                  {"$set": {'title': title, 'page_id': page_id, 'content': content, 'subtitle': subtitle}},
                                  upsert=True)


