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
        # '远': '遠',
        # '杂': '雜',
        # '敌': '敵',
        # '杀': 'kill',
        # '虑': '慮',
        # '叽': '嘰',
        # '耸': '聳',
        # '稳': '穩',
        # '迟': '遲',
        # '艳': '艷',
        # '迈': '邁',
        # '鉴': '鑒',
        # 'zha': '炸',
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
