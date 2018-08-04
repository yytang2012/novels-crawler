import os
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from parsel import Selector
import time
from urllib.parse import urljoin

from libs.database_api import MongoDatabase
from libs.polish import polish_content, polish_title, polish_subtitle
from userData.username_password import USERNAME_PASSWORD


class PopoSpider:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920x1080")
        self.mongoDB = MongoDatabase()
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start_download(self, urls):
        username, password = random.choice(USERNAME_PASSWORD)
        self.login_to_popo(username, password)
        for url in self.mongoDB.preprocess_urls(urls):
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
        title = sel.xpath('//h3[@class="title"]/text()').extract()[0]
        title = polish_title(title, 'popo')

        # get the content of target novel
        chapters = []
        time.sleep(0.5)
        chrome_driver.find_element_by_xpath('//*/a[contains(text(), "章回列表")]').click()
        while True:
            time.sleep(0.5)
            sel = Selector(text=chrome_driver.page_source)
            chapters += sel.xpath('//a[@class="cname"]')
            try:
                chrome_driver.find_element_by_xpath('//a/img[@src="/images/icon-page-last.png"]/..').click()
            except:
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
            time.sleep(1.0)
            print(page_id, subtitle_url, subtitle)
            chrome_driver.get(subtitle_url)
            chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sel = Selector(text=chrome_driver.page_source)
            contents = sel.xpath('//div[@id="readmask"]/div/p/text()').extract()
            cc = polish_content(contents)
            subtitle = polish_subtitle(subtitle)
            print(cc)
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
        # 'https://www.popo.tw/books/638516',
        'https://www.popo.tw/books/632948',
    ]
    repeat = 5
    while repeat > 0:
        spider = PopoSpider()
        spider.start_download(urls)
        repeat -= 1
        time.sleep(5)

