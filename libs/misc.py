"""
Created on Dec 27, 2016

@author: yytang
"""
import re

def get_spider_name(dom):
    nameList = dom.split('.')
    prefix = ('' if len(nameList) == 2 or nameList[0] == 'www' else nameList[0])
    name = nameList[-2]
    suffix = ('' if nameList[-1] == 'com' else nameList[-1])
    spider_name = prefix+name+suffix
    return spider_name

def get_spider_name_from_url(url):
    dom = re.search(r'http://([^\/]+)/', url).group(1)
    return get_spider_name(dom)