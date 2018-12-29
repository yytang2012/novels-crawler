import os
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from parsel import Selector
import time
from urllib.parse import urljoin

from libs.database_api import MongoDatabase
from libs.polish import polish_content, polish_title, polish_subtitle

from simpleSpiders.username_password import get_username_password


class PopoSpider:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920x1080")
        self.mongoDB = MongoDatabase()
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.username_password = get_username_password()

    def start_download(self, urls, username=None, password=None):
        if not username or not password:
            username, password = random.choice(self.username_password)
        # self.login_to_popo(username, password)
        self.login_to_po18(username, password)
        for url in self.mongoDB.preprocess_urls(urls, True):
            self.download_url(url)
        self.driver.quit()
        self.save_to_file()

    def download_url(self, url):
        chrome_driver = self.driver
        _mongoDB = self.mongoDB
        # 18 year old warning
        try:
            chrome_driver.get(url)
            time.sleep(0.5)
            chrome_driver.find_element_by_class_name('R-yes').click()
        except:
            pass

        sel = Selector(text=chrome_driver.page_source)
        # title = sel.xpath('//h3[@class="title"]/text()').extract()[0]
        title = sel.xpath('//h1[@class="book_name"]/text()').extract()[0]
        title = polish_title(title, 'popo')

        # get the content of target novel
        chapters = []
        time.sleep(0.5)
        # chrome_driver.find_element_by_xpath('//*/a[contains(text(), "章回列表")]').click()
        chrome_driver.find_element_by_link_text("章回列表").click()
        content_id = 1
        while True:
            time.sleep(0.5)
            content_id += 1
            sel = Selector(text=chrome_driver.page_source)
            # chapters += sel.xpath('//div[@class="clist"]/div/a')
            chapters += sel.xpath('//div[@class="l_chaptname"]/a')
            try:
                # chrome_driver.find_element_by_xpath('//a/img[@src="/images/icon-page-last.png"]/..').click()
                chrome_driver.find_element_by_xpath('//*/a[contains(text(), ">")]').click()
            except Exception as e:
                print(e)
                break

        novel_info = []
        all_pages = []
        for idx, chapter in enumerate(chapters):
            page_id = idx + 1
            all_pages.append(page_id)
            subtitle_url = chapter.xpath('@href').extract()[0]
            subtitle_url = urljoin(chrome_driver.current_url, subtitle_url)
            subtitle = chapter.xpath('text()').extract()[0]
            if not _mongoDB.page_exist(title, page_id):
                print(page_id, subtitle_url, subtitle)
                novel_info.append((page_id, subtitle_url, subtitle))
        _mongoDB.update_index(title, url, all_pages)

        for page_id, subtitle_url, subtitle in novel_info:
            print(page_id, subtitle_url, subtitle)
            chrome_driver.get(subtitle_url)
            time.sleep(3)
            chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sel = Selector(text=chrome_driver.page_source)
            contents = sel.xpath('//div[@id="readmask"]/div/p/text()').extract()
            cc = polish_content(contents)
            subtitle = polish_subtitle(subtitle)
            print(cc)
            if cc != '':
                _mongoDB.page_insert(title, page_id, cc, subtitle)

    def login_to_popo(self, username, password):
        print("start to login")
        login_url = 'https://members.popo.tw/apps/login.php'
        _driver = self.driver
        _driver.get(login_url)
        _driver.find_element_by_xpath('//input[@name="account"]').send_keys(username)
        _driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
        _driver.find_element_by_xpath('//input[@type="submit"]').click()
        print("Logged in as {username}".format(username=username))
        time.sleep(1)

    def login_to_po18(self, username, password):
        print("start to login")
        login_url = 'https://members.po18.tw/apps/login.php'
        _driver = self.driver
        _driver.get(login_url)
        _driver.find_element_by_xpath('//input[@name="account"]').send_keys(username)
        _driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
        _driver.find_element_by_xpath('//input[@type="submit"]').click()
        print("Logged in as {username}".format(username=username))
        time.sleep(1)

    def save_to_file(self):
        download_path = os.path.join(os.getcwd(), '..')
        download_path = os.path.join(download_path, 'userData')
        download_path = os.path.join(download_path, 'downloads')
        done, incomplete = self.mongoDB.combine_pages_to_novels(download_path)
        print('Done:')
        for idx, item in enumerate(done):
            print('{0}: url:{1}, title: {2}'.format(idx, item[0], item[1]))
        print('\nIncomplete:')
        for idx, item in enumerate(incomplete):
            print('{0}: url:{1}, title: {2}'.format(idx, item[0], item[1]))


if __name__ == '__main__':
    urls = [
        'https://www.po18.tw/books/638516',  # 爱欲绮梦【NP】
        # 'https://www.popo.tw/books/632948',
        # 'https://www.popo.tw/books/650718'  # 用爱发电（短篇集）
    ]

    # username, password = 'meidingdang11', 'popo2018'
    spider = PopoSpider()
    spider.start_download(urls)
