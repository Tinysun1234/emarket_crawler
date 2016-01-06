# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
import jd.settings
from myspiderbase import MySpiderBase
import logging
from urlparse import urlparse
import re

class Tmall3cSpider(MySpiderBase):
    name = "tmall3c"
    allowed_domains = ["tmall.com"]
    start_urls = (
        'https://3c.tmall.com/',
    )
    list_url_template = r'https://list.tmall.com/search_product.htm?%s'

    def parse(self, response):
#         inspect_response(response, self)
        type_names = jd.settings.GOODS_TYPE_NAMES[self.name]
        cat_sels = response.xpath('//ul[@class="J-fs-nav fs-nav"]/li/a')
        cat_names = cat_sels.xpath('./text()').extract()
        cat_urls = ['https:' + u + '&tbpm=1' for u in cat_sels.xpath('./@href').extract()]
#         print '\n'.join(map(lambda x, y: '%s : https:%s' % (x, y), cat_names, cat_urls))
        for i, cat_name in enumerate(cat_names):
            if cat_name.encode('utf8')  in type_names:
                print cat_name + ' : ' + cat_urls[i]
                yield scrapy.Request(cat_urls[i],
                                     callback=self.parse_goods_list_page,
                                     meta={'category':cat_name,
                                           'cur_page':1})
    
    def parse_goods_list_page(self, response):
        cat = response.meta['category']
        cur_page = response.meta['cur_page']
#         logging.info('Parsing ' + cat + ' goods list...')
        try:
            page_info = response.xpath('.//b[@class="ui-page-s-len"]/text()').extract()[0]
            logging.info('Now at %s for %s.' % (page_info, cat))
        except Exception as e:
            print e
#         inspect_response(response, self)        
        # next page
        next_page_url_param = response.xpath('.//a[@class="ui-page-s-next"]/@href').extract()
        next_page_url = ''
        if next_page_url_param:
            next_page_url = self.list_url_template % next_page_url_param
        if next_page_url:
            yield scrapy.Request(next_page_url,
                                 callback=self.parse_goods_list_page,
                                 meta={'category':cat,
                                       'cur_page':(cur_page + 1)})
        
