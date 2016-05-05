# -*- coding: utf-8 -*-
'''
Created on Dec 23, 2015

@author: tisun
'''

import scrapy
from jd.items import JdItem
import logging
import jd.settings
import re
from myspiderbase import MySpiderBase
from tools.icbctools import IcbcTools

class IcbcSpider(MySpiderBase):
    name = "icbc"
    allowed_domains = ['icbc.com.cn']
    

    site_charset = 'utf8'
    current_page = 1
    allsort_url = r'http://mall.icbc.com.cn/getAllDisplayCategoryList.jhtml'
    list_url_prefix = r'http://mall.icbc.com.cn'
    goods_url_prefix = r'http://mall.icbc.com.cn'
    price_url_prefix = r''
    comment_count_url_prefix = r''
    start_urls = (
        allsort_url,
    )
    
        
    def parse(self, response):
        return self.get_goods_type_in_allsort_page(response)

    def get_goods_type_in_allsort_page(self, response):
        '''
        获取商品类别列表
        '''
        type_names = jd.settings.GOODS_TYPE_NAMES['icbc'];
        type_sel_list = []
        all_type_sels = response.xpath('//div[@class="cate_map"]//li')
        for type_sel in all_type_sels:
            this_type_name = type_sel.xpath('.//a/text()').extract()[0]
            if  this_type_name.encode('utf8') in type_names:
                type_sel_list += type_sel.xpath('.//a')
        
#         logging.info('%d types in page!' % len(type_sel_list))
        type_title_list = [type_sel.xpath('./text()').extract()[0].encode('utf8') for type_sel in type_sel_list]
        type_url_list = [self.list_url_prefix + type_sel.xpath('./@href').extract()[0].encode('utf8') for type_sel in type_sel_list]
        type_tuple = zip(type_title_list, type_url_list)

        for type_item in type_tuple:
            type_title = type_item[0]
            type_url = type_item[1]
            logging.debug('type_title:%s\ttype_url:%s' % (type_title, type_url))
            yield scrapy.Request(type_url, \
                                callback=self.parse_goods_list_page, \
                                meta={'cur_page':1, 'category':type_title})
    
    def parse_goods_list_page(self, response):
        '''
        解析当前页面内所有商品属性
        '''
        cur_page = response.meta['cur_page']
        category = response.meta['category']
        # 获取当前页面所有商品链接并生成request_list
        glist = response.xpath('//div[@id="search_list"]//div[@class="pro"]')
        
        # 当前页面无商品
        if not glist:
            logging.info('No more goods for ' + category + ' at page ' + str(cur_page) + ' !')
            return
        
        te = response.xpath('//span[@class="search_page fr"]/text()').extract()[0] 
        total_page = int(re.search(r'/(\d+)', te).group(1))
        logging.info('Now at page %d/%d for %s' % (cur_page, total_page , category))
 
        for g_sel in glist:
            item = JdItem()
            item['name'] = g_sel.xpath('.//div[@class="p-name"]/a/@title').extract()[0]
            item['market'] = 'ICBC'
            item['idInMarket'] = g_sel.xpath('./input[@id="prod_id"]/@value').extract()[0]
            item['url'] = self.goods_url_prefix + g_sel.xpath('.//div[@class="p-name"]/a/@href').extract()[0]
            price_str = g_sel.xpath('./div[@class="p-price"]/text()').extract()[1]
            price_str = re.search(r'[,.0-9]+', price_str.encode('utf8').strip()).group(0)
            price_str.replace(',', '')
            item['price'] = float(price_str)
            item['comment'] = IcbcTools.get_comment(item['idInMarket'])
            item['pics'] = g_sel.xpath('.//img/@src').extract()[0]
            item['updateTime'] = IcbcTools.get_timestamp()
            item['category'] = category
            item['shop'] = g_sel.xpath('./div[@class="p-shop"]/a/@title').extract()[0]
            yield item
            

        # 生成下一页的request
        if cur_page < total_page:
            yield scrapy.FormRequest(response.url, callback=self.parse_goods_list_page, \
                                 formdata={'currentPage':str(cur_page + 1)}, \
                                 meta={'cur_page':(cur_page + 1), 'category':category}) 
        else:
            logging.info('Complete crawling %s' % category)    



