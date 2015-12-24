# -*- coding: utf-8 -*-

'''
Created on Dec 23, 2015

@author: tisun
'''
from toolsbase import ToolsBase, RanUAProxy
import urllib2
import re

class IcbcTools(ToolsBase):
    # id
    comment_url_template = r'http://mall.icbc.com.cn/products/productEvaluations.jhtml?productId=%s'
    
    @classmethod
    @RanUAProxy
    def get_comment(cls, goods_id, opener=None):
        if opener is None:
            opener = urllib2.build_opener()
            
        comment_url = cls.comment_url_template % goods_id
        try:
            rawpage = opener.open(comment_url).read()
            comment_dict = dict()
            comment_dict['goodComment'] = int(re.search(r'好评\((\d+)\)', rawpage).group(1))
            comment_dict['fairComment'] = int(re.search(r'中评\((\d+)\)', rawpage).group(1))
            comment_dict['badComment'] = int(re.search(r'差评\((\d+)\)', rawpage).group(1))
            comment_dict['commentWithPics'] = 0
            return comment_dict
        except Exception:
            return dict()

