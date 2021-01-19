#!/usr/bin/env python
# coding=utf-8
"""
Created on Mar 21, 2016

@author: yytang
"""
import os

import re

from libs.misc import load_from_json
from libs.misc import save_to_json
from zhconv import convert

from scrapy.utils.project import get_project_settings
settings = get_project_settings()


def polish_string(title, useless_ending='xxx'):
    """Return a safe directory name."""
    title = re.sub("《|》", "", title).strip()
    title = re.sub("[/\\\?\|<>:\"\*]", "_", title).strip()
    uselessEndings = [".txt", "txt", '全文阅读', '最新章节', useless_ending]
    # for ending in uselessEndings:
    #     if title[-len(ending):] == ending:
    #         title = title[0:-len(ending)]
    for ending in uselessEndings:
        position = title.find(ending)
        position = position if position != -1 else len(title)
        # print('{0}-{1}-{2}'.format(ending, title, position))
        title = title[0:position]
    return title


def polish_title(title, spider_name, useless_ending='xxx'):
    title = polish_string(title, useless_ending=useless_ending)
    title = "{0}-{1}".format(title, spider_name)
    return title


def polish_subtitle(subtitle):
    subtitle = polish_string(subtitle)
    subtitle = '\n*********   ' + subtitle.strip() + '   *********\n\n'
    return subtitle


# def polish_pages(tmp_spider_root_dir, pages):
#     pages = [i for i in pages if not os.path.isfile(os.path.join(tmp_spider_root_dir, str(i) + '.txt'))]
#     # pages = []
#     # for i in pagesOld:
#     #     novelPath = os.path.join(tmp_spider_root_dir, str(i) + '.txt')
#     #     if not os.path.isfile(novelPath):
#     #         pages.append(i)
#     print(pages)
#     return pages


def existing_pages(tmp_spider_root_dir):
    pages = []
    pattern = r'([\d]+)\.txt'
    for file in os.listdir(tmp_spider_root_dir):
        m = re.match(pattern, file)
        if m is not None:
            pages.append(int(m.group(1)))
    return pages


def polish_content(content, num=0, word_convert=True):
    replace_dict = {
        '「': '“',
        '」': '”',
        '%e5%94%87': '唇',
        '%e8%83%b8': '胸',
        '%e5%92%ac': '咬',
        '%e9%9c%b2%e5%87%ba': '露出',
        '%e4%b9%b3': '乳',
        '%e5%ae%b3%e7%be%9e': '娇羞',
        '%e7%be%9e': '羞',
        '%e6%91%b8': '摸',
        '%e8%85%bf': '腿',
        '%e7%b2%be': '精',
        '%e5%90%bb': '吻',
        '%e8%88%8c': '舌',
        '%e8%82%a1': '股',
        '%e5%b1%81': '屁',
        '%e8%88%94': '舔',
        '%e5%90%9f': '吟',
        '%e5%aa%9a': '媚',
        '%e6%b7%ab': '淫',
        '%e8%87%80': '腹',
        '%e8%a3%b8': '裸',
        '%e7%a9%b4': '穴',
        '%e5%a8%87': '娇',
        '%e4%ba%b2': '亲',
        '%e8%84%b1': '脱',
        '%e9%a2%88': '颈',
        '%e8%8c%8e': '茎',
        '%e6%9f%94%e8%bd%af': '柔软'
    }
    enters = '\n\n'
    res = ''
    for cc in content:
        if word_convert:
            for ori_word, new_word in replace_dict.items():
                cc = cc.replace(ori_word, new_word)
        if cc.strip().strip('\r') == '':
            continue
        # res.append(cc.strip('\n\r') + enters)
        res += (cc.strip('\n\r') + enters)

    # Convert content to zh-cn
    res = convert(res, 'zh-cn')
    return res


def save_index(title, url, tmp_spider_root_dir, chapters, first_page=True):
    index_file = settings['INDEX_FILE']
    index_path = os.path.join(tmp_spider_root_dir, index_file)
    if first_page:
        urls = [url]
        data = (title, urls, chapters)
        save_to_json(data, index_path)
    else:
        (title, urls, oldChapters) = load_from_json(index_path)
        urls.append(url)
        data = (title, urls, oldChapters + chapters)
        save_to_json(data, index_path)
