from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from libs.misc import get_spider_name_from_url

process = CrawlerProcess(get_project_settings())

url = 'http://www.sto.cc/8976-1/'
start_urls = [url]
spider_name = get_spider_name_from_url(url)
process.crawl(spider_name, start_urls=start_urls)
process.start()  # the script will block here until the crawling is finished
