import os

import requests
from parsel import Selector
from urllib.parse import urljoin
from libs.polish import polish_content, polish_title, polish_subtitle


def parse_content(url):
    page = requests.get(url)
    html = page.text
    sel = Selector(text=html)
    title = sel.xpath('//title/text()').extract()[0]
    title = title.split('_')[0]
    title = polish_title(title, 'm-ifuwen')
    print(title)

    file_path = os.path.join(os.getcwd(), '..')
    file_path = os.path.join(file_path, 'userData')
    file_path = os.path.join(file_path, 'downloads')
    file_path = os.path.join(file_path, title + '.txt')
    print(file_path)
    if os.path.isfile(file_path):
        return 0

    next_page_url = sel.xpath('//div[@class="lb_mulu chapterList"]/ul/li/a/@href').extract()[0]
    next_page_url = urljoin(page.url, next_page_url)
    print(next_page_url)
    article = ''
    idx = 1
    while True:
        req = requests.get(next_page_url)
        html = req.text
        sel = Selector(text=html)
        subtitle = sel.xpath('//h1/text()').extract()[0]
        subtitle = polish_subtitle(subtitle)
        article += subtitle

        contents = sel.xpath('//div[@id="nr1"]/p/text()').extract()
        cc = polish_content(contents)
        article += cc

        tmp = sel.xpath('//div[@class="nr_page"]/table/tr')
        next_page_url = tmp.xpath('td[@class="next"]/a/@href').extract()[0]
        mulu = tmp.xpath('td[@class="mulu"]/a/@href').extract()[0]
        if next_page_url == mulu:
            break
        idx += 1
        next_page_url = urljoin(page.url, next_page_url)
        print(idx, next_page_url)

    save_to_file(file_path, article)

def save_to_file(file_path, article):
    print(article)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(article)


if __name__ == '__main__':
    url = 'https://m.ifuwen.com/novel/30264.html'
    parse_content(url)

