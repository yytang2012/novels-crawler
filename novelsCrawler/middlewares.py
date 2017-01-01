# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os
import random

from libs.misc import load_from_json
from user_agents import USER_AGENT_LIST
from scrapy.conf import settings


class NovelscrawlerDownloaderMiddleware(object):
    def __init__(self):
        self.user_agent_list = USER_AGENT_LIST

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent_list)
        if agent:
            print(agent)
            request.headers.setdefault('User-Agent', agent)


class ProxyDownloaderMiddleware(object):
    def __init__(self):
        proxy_path = os.path.expanduser(settings['PROXY_FILE'])
        self.proxy_pool = load_from_json(proxy_path)

    def process_request(self, request, spider):
        proxy = random.choice(self.proxy_pool)
        request.meta['proxy'] = 'http://{0}:{1}'.format(proxy[0], proxy[1])
        print(request.meta['proxy'])
