import os
import time

import pymongo
from pymongo import MongoClient

MONGODB_URI = 'mongodb://localhost:27017'


class MongoDatabase:
    def __init__(self):
        client = MongoClient(MONGODB_URI)
        self.db = client["Novels"]

    def preprocess_urls(self, urls, flag=False):
        novel_info = self.db["novel_info"]
        if flag:
            return urls
        new_urls = []
        for url in urls:
            novel = novel_info.find_one({'url': url})
            if not novel:
                new_urls.append(url)
            elif not os.path.isfile(novel['path']):
                novel_info.delete_one({'url': url})
                new_urls.append(url)
        return new_urls

    def page_exist(self, title, page_id):
        pages = self.db[title]
        post = pages.find_one({'page_id': page_id})
        if post:
            if post['content'] != '':
                return True
            else:
                pages.delete_many({'page_id': page_id})
        return False

    def update_index(self, title, start_url, all_pages):
        all_pages.sort()
        index = self.db['index']
        index.delete_many({'title': title})
        novel_index = {'title': title, 'url': start_url, 'pages': all_pages}
        index.insert_one(novel_index)

    def page_insert(self, title, page_id, content, subtitle):
        novel = self.db[title]
        novel.insert_one({'title': title, 'page_id': page_id, 'content': content, 'subtitle': subtitle})

    def combine_pages_to_novels(self, download_path):
        done = []
        incomplete = []
        index = self.db['index']
        novel_info = self.db['novel_info']
        for item in index.find():
            title = item['title']
            pages = item['pages']
            url = item['url']
            novel_title = self.db[title]
            if novel_title.count() == len(pages):
                novel_output = os.path.join(download_path, '{0}.txt'.format(title.strip()))
                content = ''
                for page in novel_title.find().sort('page_id', pymongo.ASCENDING):
                    content += (page['subtitle'] + page['content'])
                with open(novel_output, 'w', encoding='utf-8') as f:
                    f.write(content)
                novel_info_row = {'title': title, 'url': url, 'path': novel_output,
                                  'timestamp': time.strftime('%Y-%m-%d %X', time.localtime())}
                novel_info.find_one_and_update({'title': title}, {"$set": novel_info_row}, upsert=True)

                index.delete_one({'title': title})
                self.db[title].drop()
                done.append((url, title))
            else:
                incomplete.append((url, title))
        return done, incomplete
