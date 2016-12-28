from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.conf import settings

from libs.misc import get_spider_name_from_url, stopwatch
from collections import defaultdict
import os


class NovelsCrawler:
    crawler_process = CrawlerProcess(get_project_settings())
    _start_urls = defaultdict(lambda: [])

    def __init__(self, url_path):
        self.allowed_domains = self.get_allowed_domains(True)
        self._start_url_init(url_path)

    def get_allowed_domains(self, write_to_file=False):
        allowed_domains = []
        for spider_name in self.crawler_process.spiders.list():
            spider = self.crawler_process.spiders.load(spider_name)
            try:
                allowed_domains += spider.allowed_domains
            except Exception:
                print("{0}: allowed domain is not defined".format(spider_name))
        if write_to_file:
            with open('allowed_domains.dat', 'w') as f:
                for url in allowed_domains:
                    f.write('{0}\n'.format(url))
        return allowed_domains

    def _start_url_init(self, url_path):
        with open(url_path, 'r') as f:
            urls = [url.strip() for url in f.readlines() if len(url.strip()) != 0]
            for url in urls:
                spider_name = get_spider_name_from_url(url)
                self._start_urls[spider_name].append(url)

    def start_downloading(self):
        for spider_name, start_urls in self._start_urls.items():
            self.crawler_process.crawl(spider_name, start_urls=start_urls)
            self.crawler_process.start()


def main():
    with stopwatch('Task Complete!'):
        url_path = os.path.expanduser(settings['URL_PATH'])
        tmp_root_dir = os.path.expanduser(settings['TMP_DIR'])
        if not os.path.isdir(tmp_root_dir):
            os.makedev(tmp_root_dir)
        crawler = NovelsCrawler(url_path)
        crawler.start_downloading()


if __name__ == '__main__':
    main()
