import os

import requests
from parsel import Selector

from libs.polish import polish_content, polish_title


def parse_content(url):
    page = requests.get(url)
    html = page.text
    sel = Selector(text=html)
    title = sel.xpath('//h1/text()').extract()[0]
    title = polish_title(title, 'yushuwu')

    file_path = os.path.join(os.getcwd(), '..')
    file_path = os.path.join(file_path, 'userData')
    file_path = os.path.join(file_path, 'downloads')
    file_path = os.path.join(file_path, title + '.txt')
    print(file_path)
    if os.path.isfile(file_path):
        return 0

    article = ''
    idx = 1
    while True:
        html = page.text
        sel = Selector(text=html)
        contents = sel.xpath('//div[@id="nr1"]/p/text()').extract()
        cc = polish_content(contents)
        article += cc

        tmp = sel.xpath('//div[@class="nr_page"]/table/tr')
        next_page = tmp.xpath('td[@class="next"]/a/@href').extract()[0]
        mulu = tmp.xpath('td[@class="mulu"]/a/@href').extract()[0]
        if next_page == mulu:
            break
        page = requests.get(next_page)
        idx += 1
        print(idx, next_page)

    save_to_file(file_path, article)

def save_to_file(file_path, article):
    print(article)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(article)


if __name__ == '__main__':
    url = 'https://m.yubook.net/novel/61472/7940223.html'
    parse_content(url)

