import os
import re
import time

from parsel import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from libs import DOWNLOAD_DIR, URL_FILE
from libs.polish import polish_content, polish_title
from selenium_spider.sto import credentials


class StoSeleniumSpider:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.username = credentials[0].get("username")
        self.password = credentials[0].get("password")
        self.url_path = URL_FILE

    def start_download(self, urls=None):
        self.login()
        if not urls:
            with open(self.url_path, 'r') as f:
                urls = f.readlines()

        urls = [url.strip() for url in urls if len(url.strip()) != 0]
        for url in urls:
            self.download_url(url)
        self.driver.quit()

    def download_url(self, url):
        chrome_driver = self.driver
        # 18 year old warning
        try:
            chrome_driver.get(url)
        except:
            pass

        sel = Selector(text=chrome_driver.page_source)
        # title = sel.xpath('//h3[@class="title"]/text()').extract()[0]
        title = sel.xpath('//h1/text()').extract()[0]
        title = polish_title(title, 'sto')

        # get the content of target novel
        chapters = []
        time.sleep(0.5)
        # chrome_driver.find_element_by_xpath('//*/a[contains(text(), "章回列表")]').click()
        # chrome_driver.find_element_by_link_text("章回列表").click()
        last_page_url = sel.xpath('//div[@id="webPage"]/a[contains(text(), "最末頁")]/@href').extract()[0]
        print(last_page_url)
        m = re.match("/book-([\d]+)-([\d]+).html", last_page_url)
        novel_id = m.group(1)
        last_page = int(m.group(2))

        novel_content = ""
        for page_id in range(1, last_page + 1):
            page_url = f"https://www.sto.cx/book-{novel_id}-{page_id}.html"
            chrome_driver.get(page_url)
            page_sel = Selector(text=chrome_driver.page_source)

            contents = page_sel.xpath('//div[@id="BookContent"]/text()').extract()
            _content_str = polish_content(contents)
            print(f"{page_id}, {page_id * 100 / last_page:.2f}%")
            novel_content += _content_str
        # end loop for
        novel_path = os.path.join(DOWNLOAD_DIR, f"{title}.txt")
        with open(novel_path, 'w') as f:
            f.write(novel_content)

    def login(self):
        print("start to login")
        login_url = 'https://www.sto.cx/user/login.aspx'
        _driver = self.driver
        _driver.get(login_url)
        _driver.find_element_by_xpath('//input[@name="username"]').send_keys(self.username)
        _driver.find_element_by_xpath('//input[@name="password1"]').send_keys(self.password)
        # input.get_attribute('value')
        verification_code = input("enter verification code")
        _driver.find_element_by_xpath('//input[@name="VerificationCode"]').send_keys(verification_code)
        _driver.find_element_by_xpath('//input[@type="submit"]').click()
        print("Logged in as {username}".format(username=self.username))


if __name__ == '__main__':

    spider = StoSeleniumSpider()
    spider.start_download()
