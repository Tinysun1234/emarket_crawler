# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response
import jd.settings
from myspiderbase import MySpiderBase
import logging

class Tmall3cSpider(MySpiderBase):
    name = "tmall3c"
    allowed_domains = ["tmall.com"]
    start_urls = (
        'https://3c.tmall.com/',
    )

    def parse(self, response):
#         inspect_response(response, self)
        type_names = jd.settings.GOODS_TYPE_NAMES[self.name]
        cat_sels = response.xpath('//ul[@class="J-fs-nav fs-nav"]/li/a')
        cat_names = cat_sels.xpath('./text()').extract()
        cat_urls = ['https:' + u for u in cat_sels.xpath('./@href').extract()]
#         print '\n'.join(map(lambda x, y: '%s : https:%s' % (x, y), cat_names, cat_urls))
        for i, cat_name in enumerate(cat_names):
            if cat_name.encode('utf8')  in type_names:
#                 print cat_name + ' : ' + cat_urls[i]
                yield scrapy.Request(cat_urls[i], callback=self.parse_goods_list_page,
                                     meta={'category':cat_name,
                                           'cur_page':1})
    
    def parse_goods_list_page(self, response):
        logging.info('Parsing goods list...')
#         inspect_response(response, self)        
