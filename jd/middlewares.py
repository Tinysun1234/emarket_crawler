# -*- coding: utf-8 -*-
'''
Created on Dec 20, 2015

@author: tisun
'''

import random
# import base64
from settings import PROXY_FILE
import cPickle
import logging
import time
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""
    def __init__(self, agents):
        self.agents = agents
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))
    def process_request(self, request, spider):
        # print "**************************" + random.choice(self.agents)
        request.headers.setdefault('User-Agent', random.choice(self.agents))
    
class RandomProxyMiddleware(object):

    def process_request(self, request, spider):
#         proxy = random.choice(PROXIES)
#         if proxy['user_pass'] is not None:
#             request.meta['proxy'] = "http://%s" % proxy['ip_port']
#             encoded_user_pass = base64.encodestring(proxy['user_pass'])
#             request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
# #                 logging.info("**************ProxyMiddleware have pass************" + proxy['ip_port'])
#             return
#         else:
#                 logging.info("**************ProxyMiddleware no pass:%d***********" % (proxy['ip_port'], str(i + 1)))
        if 'proxy' in request.meta:
            return
        proxies = self.load_proxies()
        proxy = random.choice(proxies)
        proxystr = "%s://%s:%s" % (proxy['type'], proxy['ip'], proxy['port'])
        request.meta['proxy'] = proxystr
        logging.info('Using proxy : ' + proxystr)
        
    def load_proxies(self):
        '''
        get proxies from pickle file
        '''
        min = time.localtime(time.time()).tm_min
        f = open(PROXY_FILE, 'rb')
        proxies = cPickle.load(f)
        f.close()
        return proxies
        
        
