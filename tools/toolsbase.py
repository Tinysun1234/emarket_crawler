# -*- coding: utf-8 -*-
'''
Created on Dec 23, 2015

@author: tisun
'''
import random
import urllib2
import jd.settings
import time
import logging
import re

def RanUAProxy(func):
    def _RanUAProxy(*args, **kwargs):
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
    
    @classmethod
    def str2price(cls, price_str):
        try:
            price_str = re.search(r'[,.0-9]+', price_str.encode('utf8').strip()).group(0)
            price_str = price_str.replace(',', '')
            return float(price_str)
        except Exception as e:
            logging.warn('error get price due to price_str=' + price_str)
            raise e
        return 0