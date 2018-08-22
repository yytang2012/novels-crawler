import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from userData.username_password import USERNAME_PASSWORD


class PopoSpider:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920x1080")
        # self.mongoDB = MongoDatabase()
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start_checkin(self, username, password):
        self.login_to_popo(username, password)
        chrome_driver = self.driver
        chrome_driver.find_element_by_xpath('//a[contains(text(), "打卡")]').click()
        chrome_driver.quit()

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


if __name__ == '__main__':
    urls = [
        # 'https://www.popo.tw/books/638516', # 爱欲绮梦【NP】
        'https://www.popo.tw/books/632948',
    ]
    username_passwords = USERNAME_PASSWORD
    while username_passwords:
        tmp = []
        for idx, (username, password) in enumerate(username_passwords):
            try:
                popo_spider = PopoSpider()
                popo_spider.start_checkin(username, password)
                print("{0}: Done check in for {1}\n".format(idx + 1, username))
            except Exception as e:
                tmp.append((username, password))
                print("{0}: Error happened when checking in for {1}\n".format(idx + 1, username))
        username_passwords = tmp
