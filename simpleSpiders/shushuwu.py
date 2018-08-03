import os

from parsel import Selector
import requests

from libs.misc import decode_gbk
from libs.polish import polish_content, polish_title, polish_subtitle


def parse_content(url):
    page = requests.get(url)
    html = decode_gbk(page.text)
    sel = Selector(text=html)
    title = sel.xpath('//h1/text()').extract()[0]
    title = polish_title(title, 'shushuwu')
    file_path = os.path.join(os.getcwd(), '..')
    file_path = os.path.join(file_path, 'userData')
    file_path = os.path.join(file_path, 'downloads')
    file_path = os.path.join(file_path, title + '.txt')
    print(file_path)
    if os.path.isfile(file_path):
        return 0
    episoders = sel.xpath('//dl/dd/a')
    article = ''
    for idx, ep in enumerate(episoders):
        subtitle = ep.xpath('text()').extract()[0]
        href = ep.xpath('@href').extract()[0]
        url_page = url.rstrip('/') + '/' + href
        print(idx, subtitle, url_page)
        subtitle = polish_subtitle(subtitle)
        article += subtitle
        cc = parse_page(url_page)
        article += cc
    save_to_file(file_path, article)

def parse_page(url):
    page = requests.get(url)
    html = decode_gbk(page.text)
    sel = Selector(text=html)
    contents = sel.xpath('//div[@class="yd_text2"]/text()').extract()
    cc = polish_content(contents)
    return cc

def save_to_file(file_path, article):
    print(article)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(article)


if __name__ == '__main__':
    url = 'http://www.shushuwu.cc/novel/1219/'
    parse_content(url)

