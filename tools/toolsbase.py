# -*- coding: utf-8 -*-
'''
Created on Dec 23, 2015

@author: tisun
'''
import random
import urllib2
import jd.settings
import time

def RanUAProxy(func):
    def _RanUAProxy(*args, **kwargs):
#         proxy = random.choice(jd.settings.PROXIES)
#         proxy_handler = urllib2.ProxyHandler({'http':"http://%s" % proxy['ip_port']})
        ua = random.choice(jd.settings.USER_AGENTS)
        header_ua = [ ('User-Agent', ua) ]
        opener = urllib2.build_opener()
        opener.addheaders = header_ua
        kwargs['opener'] = opener
        return func(*args, **kwargs)
    return _RanUAProxy

   
class ToolsBase(object):
    '''
    工具基类
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass

    @classmethod
    def get_timestamp(cls):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))