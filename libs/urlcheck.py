# -*- coding: utf-8 -*-

"""
Created on Apr 14, 2016

@author: yytang
"""
import re


def url_check(url):
    mlwxs_pattern = 'http://m.lwxs.com/wapbook/([\d]+).html'
    if re.search(mlwxs_pattern, url) is not None:
        return 'http://m.lwxs.com/wapbook/{0}_1/'.format(re.search(mlwxs_pattern, url).group(1))

    return url

