#!/usr/bin/env python
# coding=utf-8
"""
Created on Mar 21, 2016

@author: yytang
"""
import os

from scrapy.conf import settings
import re

from libs.misc import load_from_json
from libs.misc import save_to_json


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


def polish_chapter_ids(tmp_spider_root_dir, pages):
    pages = [i for i in pages if not os.path.isfile(os.path.join(tmp_spider_root_dir, str(i) + '.txt'))]
    # pages = []
    # for i in pagesOld:
    #     novelPath = os.path.join(tmp_spider_root_dir, str(i) + '.txt')
    #     if not os.path.isfile(novelPath):
    #         pages.append(i)
    print(pages)
    return pages


def polish_content(content, num=0):
    res = []
    enters = '\n\n'
    for cc in content:
        cc = cc.replace('「', '“')
        cc = cc.replace('」', '”')
        if cc.strip().strip('\r') == '':
            continue
        res.append(cc.strip('\n\r') + enters)
    return res


def save_index(title, tmp_spider_root_dir, url, chapters, firstPage=True):
    index_file = settings['INDEX_FILE']
    index_path = os.path.join(tmp_spider_root_dir, index_file)
    if firstPage:
        urls = [url]
        data = [title, urls, chapters]
        save_to_json(data, index_path)
    else:
        [title, urls, oldChapters] = load_from_json(index_path)
        urls.append(url)
        data = [title, urls, oldChapters + chapters]
        save_to_json(data, index_path)
