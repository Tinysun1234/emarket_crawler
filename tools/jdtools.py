# -*- coding: utf-8 -*-
'''
Created on Dec 19, 2015

@author: tisun
'''
import json
import logging
import re

import time
import urllib2
import jd.settings
# import random

from toolsbase import ToolsBase, RanUAProxy

class JDTools(ToolsBase):
    '''
    JD使用
    '''
    site_charset = 'gbk'
    
    tag_url_template = r'http://club.jd.com/productpage/p-%s-s-0-t-3-p-0.html'
    stock_url_template = r'http://c0.3.cn/stock?skuId=%s&cat=%s&area=%s'
    comment_count_url_template = r'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=%s'
    promotion_url_template = r'http://cd.jd.com/promotion/v2?skuId=%s&area=%s&cat=%s'
    price_url_template = r'http://p.3.cn/prices/mgets?skuids=J_%s'
    stock_url_template = r'http://c0.3.cn/stock?skuId=%s&cat=%s&area=%s'
    hzgoodsdetail_url_template = r'http://www.boxz.com/products/360buy-%s.shtml'
    
    area_dict = {'shanghai':'2_2813_51976_0',  # 上海徐汇城区
               'beijing':'1_72_2799_0',  # 北京朝阳区三环以内
               'guangzhou':'19_1601_3633_0',  # 广东广州市天河区
               'chengdu':'22_1930_50947_0',  # 四川省成都市武侯区
               'xian':'27_2376_50235_0',  # 陕西省西安市莲湖区
               'wuhan':'17_1381_3079_0',  # 湖北省武汉市武昌区
            }
    
    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    @classmethod   
    def detect_charset(cls, response):
        the_charset = re.search(r'charset=([-a-zA-Z]+)', response.body, re.I)
        if the_charset:
            cls.site_charset = the_charset
                
    @classmethod
    def price_url(cls, goods_meta):
        return cls.price_url_template % goods_meta['skuId']
    
    @classmethod
    def price_parser(cls, raw):
        price_str = cls.convert_to_utf8(raw)
        prices_json = json.loads(str(price_str))
#         logging.info(prices_json)
        return float(prices_json[0]['p'])
    
    @classmethod
    @RanUAProxy
    def get_price(cls, goods_meta, opener=None):  
        try:
            if not opener:
                opener = urllib2.build_opener()
                
            price_url = cls.price_url(goods_meta)
            # logging.debug('price url:' + price_url)
            raw = opener.open(price_url, timeout=jd.settings.AJAX_TIMEOUT).read()
            return cls.price_parser(raw)
        
        except Exception as e:
            logging.warn('Failed to get price due to ' + str(e) + ' at ' + price_url)
            return None
            
            
    @classmethod
    def convert_to_utf8(cls, rawstr):
        try:
            s = rawstr.decode(cls.site_charset).encode('utf8')
        except Exception:
            logging.debug('codec failed: ' + rawstr)   
            return rawstr
        logging.debug('codec succ: ' + s)
        return s

    @classmethod
    def promotion_url(cls, goods_meta):
        return cls.promotion_url_template % \
                (goods_meta['skuId'], cls.area_dict['beijing'], goods_meta['cat'])
    @classmethod
    def promotion_parser(cls, raw):
        prom_tmp = cls.convert_to_utf8(raw)
        prom_json = json.loads(prom_tmp)
        prom_items = prom_json['prom']['pickOneTag']
        return [pi['name'] + ':' + pi['content'] for pi in prom_items]        
    @classmethod
    @RanUAProxy
    def get_promotion(cls, goods_meta, opener=None):
        '''
        解析并获取促销信息
        '''
        try:
            if not opener:
                opener = urllib2.build_opener()
                
            promotion_url = cls.promotion_url(goods_meta)
            raw = opener.open(promotion_url, timeout=jd.settings.AJAX_TIMEOUT).read()
            return cls.promotion_parser(raw)
        except Exception as e:
            logging.warn('Failed to get promotions due to ' + str(e) + ' at ' + promotion_url)
            return []
        
    @classmethod
    def comment_url(cls, goods_meta):
        return cls.comment_count_url_template % goods_meta['skuId']
    @classmethod
    def comment_parser(cls, raw):
        comment_json = json.loads(raw)
        comment_dict = comment_json['CommentsCount'][0]
        return {'goodComment':comment_dict['GoodCount'],
                'fireComment':comment_dict['GeneralCount'],
                'badComment':comment_dict['PoorCount'],
                'commentWithPics':comment_dict['ShowCount']
                }
    @classmethod
    @RanUAProxy
    def get_comment(cls, goods_meta, opener=None):
        '''
        解析并获取评论数信息
        '''
        try:
            if not opener:
                opener = urllib2.build_opener()
                
            comment_url = cls.comment_url(goods_meta)
            logging.debug(comment_url)
            raw = opener.open(comment_url, timeout=jd.settings.AJAX_TIMEOUT).read()
            return cls.comment_parser(raw)
        except Exception as e:
            logging.warn('Failed to get comments due to ' + str(e) + ' at ' + comment_url)
            return dict()
    
    @classmethod
    def tags_url(cls, goods_meta):
        return cls.tag_url_template % goods_meta['skuId']
    @classmethod
    def tags_parser(cls, raw):
        tags_tmp = cls.convert_to_utf8(raw)
        tags_json = json.loads(tags_tmp)['hotCommentTagStatistics']
        tags_list = [tag_st['name'] for tag_st in tags_json]
        return tags_list
    @classmethod
    @RanUAProxy
    def get_tags(cls, goods_meta, opener=None):
        '''
        返回评价标签数组
        '''
        try:
            if not opener:
                opener = urllib2.build_opener()
            
            tags_url = cls.tags_url(goods_meta)
            raw = opener.open(tags_url, timeout=jd.settings.AJAX_TIMEOUT).read()
            return cls.tags_parser(raw)
        except Exception as e:
            logging.warn('Failed to get tags due to ' + str(e) + ' at ' + tags_url)
            return None

        
    @classmethod
    def stock_url(cls, goods_meta, city='beijing'):
        return cls.stock_url_template % \
                    (goods_meta['skuId'], goods_meta['cat'], cls.area_dict[city])
    @classmethod
    def stock_parser(cls, raw):
        stock_tmp = cls.convert_to_utf8(raw)
        stock_json = json.loads(stock_tmp)
        return stock_json['stock']['StockStateName']        
    @classmethod
    @RanUAProxy
    def get_stock(cls, goods_meta, opener=None):
        '''
        获取6个城市的库存信息
        '''
        try:
            if not opener:
                opener = urllib2.build_opener()
            stock = dict()
            for city in cls.area_dict:
                stock_url = cls.stock_url(goods_meta, city)
                raw = opener.open(stock_url, timeout=jd.settings.AJAX_TIMEOUT).read()
                stock[city] = cls.stock_parser(raw)
            logging.debug('stock' + str(stock))
            return stock
        except Exception as e:
            logging.warn('Failed to get stock due to ' + str(e) + ' at ' + stock_url)
            return dict()
    
    @classmethod
    def get_pics(cls, goods_info_sel):
        '''
        获取图片列表
        '''
        try:
            pics_tmp = goods_info_sel.xpath('//div[@class="spec-items"]//img/@src').extract()
            return ['http:' + re.sub(r'/n5/', r'/n1/', picurl) for picurl in pics_tmp]
        except Exception as e :
            logging.warn('Failed to get pics due to ' + str(e))
            return []     

    @classmethod
    @RanUAProxy
    def get_history_price(cls, goods_meta, opener=None):
        '''
        从盒子网获取历史数据
        '''
        try:
            if not opener:
                opener = urllib2.build_opener()
            hz_url = cls.hzgoodsdetail_url_template % goods_meta['skuId']
            his_page = opener.open(hz_url, timeout=jd.settings.AJAX_TIMEOUT).read()
            value_tmp1 = re.search(r'chart_data" value="([^"]+)"', his_page).group(1)
            value_tmp2 = re.sub(r'x', r"'x'", value_tmp1)
            value = re.sub(r'y', r"'y'", value_tmp2)
            history_price_list_raw = eval(value)
            history_price_dict = dict()
            for price_raw in history_price_list_raw:
                time_plot = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(price_raw['x']) / 1000))    
                price = float(price_raw['y'])
                history_price_dict[time_plot] = price
            return history_price_dict
        except Exception:
#             logging.warn('Failed to get history price due to ' + str(e))
            return dict()
            
    @classmethod
    def get_shop(cls, response):
        shop_sel = response.xpath('//ul[@id="parameter2"]/li')[2]
        try:
            if '店铺'.decode('utf8') in \
                shop_sel.xpath('./text()').extract()[0]:
                return cls.convert_to_utf8(shop_sel.xpath('./@title').extract()[0])
            else:
                return cls.convert_to_utf8('京东自营')
        except Exception:
            return cls.convert_to_utf8('京东自营') 
        
        
            
                
        
    
        
