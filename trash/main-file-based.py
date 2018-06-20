import shutil
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.conf import settings

from libs.dropbox_api import DropboxAPI
from libs.misc import *
from collections import defaultdict
import os

from trash.urlcheck import url_check


class NovelsCrawler:
    crawler_process = CrawlerProcess(get_project_settings())

    # _start_urls = defaultdict(lambda: [])

    def __init__(self):
        self._start_urls = defaultdict(lambda: [])
        self.init_directories()
        self.allowed_domains = self.get_allowed_domains(True)

    def init_directories(self):
        self.root_dir = settings['ROOT_DIR']
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        self.tmp_novels_dir = settings['TMP_DIR']
        if not os.path.isdir(self.tmp_novels_dir):
            os.makedirs(self.tmp_novels_dir)
        self.url_path = settings['URL_FILE']
        self.log_path = settings['LOG_PATH']
        self.downloads_path = settings['DOWNLOADS']
        if not os.path.isdir(self.downloads_path):
            os.makedirs(self.downloads_path)
        self.index = settings['INDEX_FILE']
        token_path = settings['DROPBOX_TOKEN']
        [self.token] = load_from_json(token_path)


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
        # 1. Remove the spaces
        # 2. Convert the urls to supported format
        # 3. Remove the urls not supported
        urls = [url.strip() for url in urls if len(url.strip()) != 0]
        urls = [url_check(url) for url in urls]
        urls = [url for url in urls if get_domain_from_url(url) in self.allowed_domains]
        self._start_urls = defaultdict(lambda: [])

        for url in urls:
            spider_name = get_spider_name_from_url(url)
            self._start_urls[spider_name].append(url)

    def start_downloading(self, save_to_Dropbox=True):
        for spider_name, start_urls in self._start_urls.items():
            try:
                self.crawler_process.crawl(spider_name, downloads_dir=self.downloads_path, start_urls=start_urls, tmp_novels_dir=self.tmp_novels_dir)
            except KeyError:
                """ we remove the m prefix of the spider_name """
                prefix_separator, suffix_separator = get_name_separators()
                prefix_separator_pos = spider_name.find(prefix_separator)
                if prefix_separator_pos == 0:
                    spider_name = 'm' + spider_name
                else:
                    spider_name = spider_name[prefix_separator_pos:]
                self.crawler_process.crawl(spider_name, downloads_dir=self.downloads_path, start_urls=start_urls, tmp_novels_dir=self.tmp_novels_dir)
        self.crawler_process.start()
        print("Stage: start combining pages to novels")
        novels = self.combine_pages_to_novels()
        if len(novels) != 0:
            if save_to_Dropbox:
                self.upload_to_dropbox(novels)
            else:
                self.update_local_log(novels)

        def flatten(urls):
            return sum(urls, [])

        successful_urls = flatten([item[1] for item in novels])
        all_urls = flatten(self._start_urls.values())
        failed_urls = [url for url in all_urls if url not in successful_urls]
        return failed_urls

    def combine_pages_to_novels(self):
        """
         1. Traverse the root directory and identify the novels
         2. Read the metadata from index file
         3. Combine the pages into novels and store them to Downloads directory
         4. Remove the temporary directories
        :return:
        """
        novels = []
        for title in os.listdir(self.tmp_novels_dir):
            novel_dir = os.path.join(self.tmp_novels_dir, title)
            novel_output = os.path.join(self.downloads_path, '{0}.txt'.format(title))
            if os.path.isdir(novel_dir):
                index_path = os.path.join(novel_dir, self.index)
                data = load_from_json(index_path)
                if data is None:
                    continue
                else:
                    (title, urls, pages) = data
                    contents = '{0}\n\n'.format(title)
                    for page in pages:
                        page_path = os.path.join(novel_dir, '{0}.txt'.format(page))
                        try:
                            with open(page_path, 'r', encoding='utf-8') as f:
                                contents += f.read()
                        except Exception:
                            contents = ''
                            break
                    if len(contents) != 0:
                        with open(novel_output, 'w', encoding='utf-8') as f:
                            f.write(contents)
                        shutil.rmtree(novel_dir)
                        novels.append((title, urls))
        return novels

    def update_local_log(self, novels):
        # update the history log
        try:
            with open(self.log_path, 'r') as f:
                log_content = f.read()
        except Exception:
            log_content = ''

        curTime = time.strftime('%Y-%m-%d %X', time.localtime())
        new_log = "+++++++++++++++++++++++++   " + curTime + "   ++++++++++++++++++++++++++\n"

        for item in novels:
            (title, urls) = item
            new_log += "\t%-30s\t%-s\n" % (title, urls)
        log_content = '{0}\n{1}'.format(new_log, log_content)

        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)

    def upload_to_dropbox(self, novels):
        dbx_api = DropboxAPI(self.token)
        logfile = settings['LOG']
        # Download old log from Dropbox
        log_content = dbx_api.download('', 'Configuration', logfile)
        # log_content = log_content.decode('utf-8')

        # Generate the new log and write it to local log
        curTime = time.strftime('%Y-%m-%d %X', time.localtime())
        new_log = "+++++++++++++++++++++++++   " + curTime + "   ++++++++++++++++++++++++++\n"
        for item in novels:
            (title, urls) = item
            new_log += "\t%-30s\t%-s\n" % (title, urls)
        log_content = '{0}\n{1}'.format(new_log, log_content)
        with open(self.log_path, 'w') as f:
            f.write(log_content)

        # Upload the new log to Dropbox
        dbx_api.upload(self.log_path, '', 'Configuration', logfile, overwrite=True)

        # Upload the novels to Dropbox
        for item in novels:
            (title, urls) = item
            output_path = os.path.join(self.downloads_path, title + '.txt')
            dbx_api.upload(output_path, '', '', title + '.txt', overwrite=True)


def main(count=0, urls=None):
    with stopwatch('Main'):
        crawler = NovelsCrawler()
        crawler.start_url_init(urls)
        failed_urls = crawler.start_downloading()
        print(failed_urls)


if __name__ == '__main__':
    main()
