import contextlib
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from libs.email_api import EmailAPIs


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))


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


def popo_checkin():
    username_passwords = []
    with open('username_password.txt', encoding="utf8") as f:
        for line in f.readlines():
            segments = line.split(',')
            if len(segments) < 2:
                continue
            username = segments[0].strip()
            password = segments[1].strip()
            username_passwords.append((username, password))
    # username_passwords = USERNAME_PASSWORD
    print(username_passwords)
    message_log = ''
    with stopwatch('popo check in'):
        while username_passwords:
            tmp = []
            for idx, (username, password) in enumerate(username_passwords):
                try:
                    popo_spider = PopoSpider()
                    popo_spider.start_checkin(username, password)
                    tmp_msg = "{0}: Done check in for {1}\n".format(idx + 1, username)
                    message_log += tmp_msg
                    print(tmp_msg)
                except Exception as e:
                    tmp.append((username, password))
                    tmp_msg = "{0}: Error happened when checking in for {1}\n".format(idx + 1, username)
                    message_log += tmp_msg
                    print(tmp_msg)
            username_passwords = tmp
    notification(message_log)


def notification(body):
    MY_EMAIL = 'xxxxx@gmail.com'
    PASSWORD = 'password'
    try:
        email = EmailAPIs(MY_EMAIL, PASSWORD)
        subject = datetime.datetime.now().strftime('%Y-%m-%d %H:%M ') + 'Check-in is completed'
        destination_address = 'lingyingchao94zoe@gmail.com'
        email.send_message_to_one(destination_address, subject, body)
        print('message has been sent successfully')
    except Exception as e:
        print("Error happened when trying to send the message")
    print('We have completed check in for all accounts')


if __name__ == '__main__':
    flag = True
    while True:
        current_time = datetime.datetime.now().strftime('%H')
        current_time = int(current_time)
        if current_time <= 12 and not flag:
            flag = True
        if current_time > 12 and flag:
            popo_checkin()
            flag = False
        time.sleep(60 * 10)
