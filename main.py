from collections import defaultdict

import pymongo
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from libs.dropbox_api import DropboxAPI
from libs.misc import *


class NovelsCrawler:
    crawler_process = CrawlerProcess(get_project_settings())

    # _start_urls = defaultdict(lambda: [])

    def __init__(self, urls):
        self._start_urls = defaultdict(lambda: [])
        self.initialization()
        self.allowed_domains = self.get_allowed_domains(True)
        self.start_url_init(urls)

    def initialization(self):
        self.url_path = settings['URL_FILE']
        self.downloads_path = settings['DOWNLOADS']
        if not os.path.isdir(self.downloads_path):
            os.makedirs(self.downloads_path)

        """ Initialize from configuration file """
        config_dir = settings['CONFIGURATION']
        config_path = os.path.join(config_dir, 'config.ini')
        if not os.path.isfile(config_path):
            config_path = os.path.join(config_dir, 'config_default.ini')
        import configparser
        with open(config_path) as f:
            config = configparser.RawConfigParser(allow_no_value=True)
            config.read_file(f)
            self.token = config.get('dropbox', 'token')

    def get_allowed_domains(self, write_to_file=False):
        allowed_domains = []
        for spider_name in self.crawler_process.spiders.list():
            spider = self.crawler_process.spiders.load(spider_name)
            try:
                allowed_domains += spider.allowed_domains
            except Exception:
                print("{0}: allowed domain is not defined".format(spider_name))
        allowed_domains.sort()
        if write_to_file:
            with open('allowed_domains.dat', 'w') as f:
                for url in allowed_domains:
                    f.write('{0}\n'.format(url))
        return allowed_domains

    def start_url_init(self, urls=None):
        if not urls:
            with open(self.url_path, 'r') as f:
                urls = f.readlines()

        urls = [url.strip() for url in urls if len(url.strip()) != 0]
        self._start_urls = defaultdict(lambda: [])

        for url in urls:
            spider_name = get_spider_name_from_url(url)
            self._start_urls[spider_name].append(url)

    def start_downloading(self, save_to_Dropbox=True):
        for spider_name, start_urls in self._start_urls.items():
            try:
                self.crawler_process.crawl(spider_name, downloads_dir=self.downloads_path, start_urls=start_urls)
            except KeyError:
                """ we remove the m prefix of the spider_name """
                prefix_separator, suffix_separator = get_name_separators()
                prefix_separator_pos = spider_name.find(prefix_separator)
                if prefix_separator_pos == 0:
                    spider_name = 'm' + spider_name
                else:
                    spider_name = spider_name[prefix_separator_pos:]
                self.crawler_process.crawl(spider_name, downloads_dir=self.downloads_path, start_urls=start_urls)
        self.crawler_process.start()
        print("Stage: start combining pages to novels")
        done, incomplete = self.combine_pages_to_novels()

        if len(done) != 0:
            if save_to_Dropbox:
                self.upload_to_dropbox(done)

        return done, incomplete

    def combine_pages_to_novels(self):
        done = []
        incomplete = []
        client = MongoClient(settings['MONGODB_URI'])
        db = client["Novels"]
        index = db['index']
        novel_info = db['novel_info']
        for item in index.find():
            title = item['title']
            pages = item['pages']
            url = item['url']
            novel_title = db[title]
            if novel_title.count() == len(pages):
                novel_output = os.path.join(self.downloads_path, '{0}.txt'.format(title))
                content = ''
                for page in novel_title.find().sort('page_id', pymongo.ASCENDING):
                    content += (page['subtitle'] + page['content'])
                with open(novel_output, 'w', encoding='utf-8') as f:
                    f.write(content)
                novel_info_row = {'title': title, 'url': url, 'path': novel_output,
                                  'timestamp': time.strftime('%Y-%m-%d %X', time.localtime())}
                novel_info.find_one_and_update({'title': title}, {"$set": novel_info_row}, upsert=True)

                index.delete_one({'title': title})
                db[title].drop()
                done.append((url, title))
            else:
                incomplete.append((url, title))
        return done, incomplete

    def upload_to_dropbox(self, novels):
        dbx_api = DropboxAPI(self.token)

        # Upload the novels to Dropbox
        for item in novels:
            (url, title) = item
            output_path = os.path.join(self.downloads_path, title + '.txt')
            dbx_api.upload(output_path, '', '', title + '.txt', overwrite=True)


def main(urls=None):
    with stopwatch('Main'):
        crawler = NovelsCrawler(urls)
        done, incomplete = crawler.start_downloading()
        print('Done:')
        for idx, item in enumerate(done):
            print('{0}: url:{1}, title: {2}'.format(idx, item[0], item[1]))
        print('\nIncomplete:')
        for idx, item in enumerate(incomplete):
            print('{0}: url:{1}, title: {2}'.format(idx, item[0], item[1]))


if __name__ == '__main__':
    main()
