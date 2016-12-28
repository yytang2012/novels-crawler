# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os


class NovelsCrawlerPipeline(object):
    def process_item(self, item, spider):
        if item['type'] == 'comics':
            return item

        page_id = item['id']
        subtitle = item['subtitle']
        content = item['content']
        root_dir = item['root_dir']
        novel_path = os.path.join(root_dir, str(page_id) + '.txt')
        if not os.path.isfile(novel_path):
            with open(novel_path, 'w') as fd:
                print(subtitle)
                fd.write(subtitle.encode('utf-8'))
                for cc in content:
                    fd.write(cc.encode('utf-8'))

