# -*- coding: utf-8 -*-
'''
Created on Dec 20, 2015

@author: tisun
'''
import threading
from tools.jdtools import JDTools 

class TagThread(threading.Thread):
    '''
    获取标签线程类
    '''
    def __init__(self, goods_meta):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)  
        self.goods_meta = goods_meta
    def run(self):
        self.ret = JDTools.get_tags(self.goods_meta)
        