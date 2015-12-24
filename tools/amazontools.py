# -*- coding: utf-8 -*-
'''
Created on Dec 24, 2015

@author: tisun
'''
import re
import urllib2
from toolsbase import ToolsBase, RanUAProxy
import time
import jd.settings
import logging

class AmazonTools(ToolsBase):
    '''
    classdocs
    '''
    hzgoodsdetail_url_template = r'http://www.boxz.com/products/amazon-%s.shtml'
    
    def __init__(self, params):
        '''
        Constructor
        '''
    # id
    comment_url_template = r'http://www.amazon.cn/review/widgets/average-customer-review/popover/ref=acr_search__popover?ie=UTF8&asin=%s&contextId=search&ref=acr_search__popover'
    
    @classmethod
    def get_price(cls, goods_sel):
        '''
        获取多个商品的价格信息，并返回一个列表
        '''
        prices = []
        for good_sel in goods_sel:
            price_elem = good_sel.xpath('.//span[@class="a-size-base a-color-price s-price a-text-bold"]/text()')
            if not price_elem:
                price_elem = good_sel.xpath('.//span[@class="a-size-base a-color-price a-text-bold"]/text()')
                
            if price_elem:
#                     raise ValueError('No price for item: %s' % good_sel.xpath('.//a[@class="a-link-normal s-access-detail-page  a-text-normal"]/@title').extract()[0].encode('utf8'))
                prices.append(float(re.search(r'[.0-9]+', price_elem.extract()[0].replace(',', '')).group(0)))
            else:
                prices.append(float(-1))
        return prices

    @classmethod
    def get_promote(cls, goods_sel):
        '''
        获取促销信息，并返回一个列表
        '''
        promotes = []
        for good_sel in goods_sel:
            promote = good_sel.xpath('.//div[@class="a-row a-spacing-top-mini a-spacing-mini"]//span[@class="a-color-secondary"]/text()').extract()
            promote += good_sel.xpath('.//div[@class="a-row a-spacing-top-mini a-spacing-mini"]//span[@class="a-list-item"]/text()').extract()
#             promote = '#'.join(promote)
            promotes.append(promote)
        return promotes
    
    @classmethod
    @RanUAProxy
    def get_comment(cls, goods_sel, opener=None):
        '''
        获取评论数，并返回一个列表
        '''
        if not opener:
            opener = urllib2.build_opener()
            
        ids = goods_sel.xpath('@data-asin').extract()
        comments = []
        for goods_id in ids:
            comment_url = cls.comment_url_template % goods_id
            try:
                comment_page = opener.open(comment_url).read()
                matches = re.findall(r'>(\d+)<', comment_page)
                if len(matches) is 5:
                    comment_raw = [int(m) for m in matches]
                    one_comment = {'goodComment':comment_raw[0],
                              'fairComment':comment_raw[1] + comment_raw[2],
                              'badComment':comment_raw[3] + comment_raw[4]}
                    comments.append(one_comment)
            except Exception:
                comments.append(dict())
        return comments
            
            
    @classmethod
    @RanUAProxy
    def get_histories_stock(cls, ids, opener=None):
        '''
        从盒子网获取历史数据和库存信息
        '''
        history_price_list = []
        stock_list = []

        for goods_id in ids:
            
            if not opener:
                opener = urllib2.build_opener()
            try:
                hz_url = cls.hzgoodsdetail_url_template % goods_id
                his_page = opener.open(hz_url, timeout=jd.settings.AJAX_TIMEOUT).read()
            except Exception:
#                 logging.warn('Failed to get history due to ' + str(e))
                history_price_list.append(dict())
                stock_list.append('')
                continue
                
            # history
            try:
                value_tmp1 = re.search(r'chart_data" value="([^"]+)"', his_page).group(1)
                value_tmp2 = re.sub(r'x', r"'x'", value_tmp1)
                value = re.sub(r'y', r"'y'", value_tmp2)
                history_price_list_raw = eval(value)
                history_price_dict = dict()
                for price_raw in history_price_list_raw:
                    time_plot = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(price_raw['x']) / 1000))    
                    price = float(price_raw['y'])
                    history_price_dict[time_plot] = price
                history_price_list.append(history_price_dict)
            except AttributeError:
                history_price_list.append(dict())
                
            # stock
            try:
                stock_list.append(re.search(r'库存：</span>\s*<span>([^<]+)<', his_page).group(1))
            except AttributeError:
                stock_list.append('')

        return history_price_list, stock_list
        
            
            
