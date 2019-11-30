import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from parsel import Selector
import time
from urllib.parse import urljoin

from simpleSpiders.utils import get_username_password

# login_url = 'https://members.popo.tw/apps/login.php'
login_url = 'https://members.po18.tw/apps/login.php'


class PopoSpider:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.username_password = get_username_password()

    def start_download(self, urls):
        username, password = random.choice(self.username_password[15:])
        self.login_to_popo(username, password)
        for url in urls:
            self.download_url(url)
        self.driver.quit()

    def download_url(self, url):
        chrome_driver = self.driver
        # 18 year old warning
        try:
            chrome_driver.get(url)
            time.sleep(8)
            # chrome_driver.find_element_by_class_name('R-yes').click()
        except:
            pass

        sel = Selector(text=chrome_driver.page_source)
        title = sel.xpath('//h1[@class="book_name"]/text()').extract()[0]
        print(title)
        # title = polish_title(title, 'popo')

        # get the content of target novel
        chapters = []
        time.sleep(0.5)
        chrome_driver.find_element_by_xpath('//*/a[contains(text(), "章回列表")]').click()
        while True:
            time.sleep(0.5)
            sel = Selector(text=chrome_driver.page_source)
            chapters += sel.xpath('//div[@class="l_chaptname"]/a')
            try:
                chrome_driver.find_element_by_xpath('//a[@class="num" and contains(text(), ">")]').click()
            except:
                break
        print(chapters)

        novel_info = []
        all_pages = []
        for idx, chapter in enumerate(chapters):
            page_id = idx + 1
            all_pages.append(page_id)
            subtitle_url = chapter.xpath('@href').extract()[0]
            subtitle_url = urljoin(chrome_driver.current_url, subtitle_url)
            subtitle = chapter.xpath('text()').extract()[0]
            novel_info.append((page_id, subtitle_url, subtitle))
        count = 5
        while count > 0:
            for page_id, subtitle_url, subtitle in novel_info:
                time.sleep(3)
                print(page_id, subtitle_url, subtitle)
                chrome_driver.get(subtitle_url)
                chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sel = Selector(text=chrome_driver.page_source)
                contents = sel.xpath('//div[@id="readmask"]/div/p/text()').extract()
                print(contents)

    def login_to_popo(self, username, password):
        print("start to login")
        _driver = self.driver
        _driver.get(login_url)
        _driver.find_element_by_xpath('//input[@name="account"]').send_keys(username)
        _driver.find_element_by_xpath('//input[@type="password"]').send_keys(password)
        _driver.find_element_by_xpath('//input[@type="submit"]').click()
        print("Logged in as {username}".format(username=username))
        time.sleep(1)


if __name__ == '__main__':
    urls = [
        # 'https://www.po18.tw/books/638516',  # 爱欲绮梦【NP】
        # 'https://www.popo.tw/books/632948', # 女巫安娜
        # 'https://www.popo.tw/books/616424',  # 鏡之國
        # 'https://www.popo.tw/books/653169', # 如果你知我心
        'https://www.po18.tw/books/665458',  # 无颜（H）1vs1
    ]
    repeat = 100
    while repeat > 0:
        try:
            spider = PopoSpider()
            spider.start_download(urls)
            repeat -= 1
        except Exception as e:
            print("Something went wrong: {}".format(e))
        finally:
            time.sleep(5)
