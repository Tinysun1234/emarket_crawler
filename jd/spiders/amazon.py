# -*- coding: utf-8 -*-
'''
Created on Dec 24, 2015

@author: tisun
'''
import scrapy
import jd.settings
import logging
from myspiderbase import MySpiderBase
from tools.amazontools import AmazonTools
from jd.items import JdItem
# from scrapy.shell import inspect_response

class AmazonSpider(MySpiderBase):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    start_urls = (
        'http://www.amazon.cn/gp/site-directory/',
    )
    
    # url suffix
    goods_list_url_template = r'http://www.amazon.cn%s'
    
    
    def parse(self, response):
        return self.get_goods_type_in_allsort_page(response)
    
    def get_goods_type_in_allsort_page(self, response):
        '''
        生成指定大类型下的小类型请求
        '''
        type_names = jd.settings.GOODS_TYPE_NAMES['amazon']
        logging.info('#'.join(type_names))
        major_cat_sels = response.xpath('//div[@class="a-row a-spacing-small a-spacing-top-medium"]')
        req_list = []
        for major_sel in major_cat_sels:
            major_names = major_sel.xpath('.//div[@class="a-row a-spacing-extra-large a-spacing-top-small"]//a[@class="nav_a a-link-normal a-color-base"]/text()').extract()
            major_name = ''.join(major_names)
            if major_name.encode('utf8') in type_names:
                logging.info(major_name)
                minor_cat_sels = major_sel.xpath('.//li[@class="a-spacing-small"]')
                cats_name = [cat_name for cat_name in minor_cat_sels.xpath('.//a/text()').extract()]
                cats_url = [self.goods_list_url_template % cat_url for cat_url in minor_cat_sels.xpath('.//a/@href').extract()]
                func_request = lambda x, y: scrapy.Request(x,
                                                           callback=self.parse_goods_list_page,
                                                           meta={'cat':y, 'cur_page':1})
                req_list += map(func_request, cats_url, cats_name)
        return req_list

    def parse_goods_list_page(self, response):
        '''
        商品列表页
        '''
#         print 'In parse_goods_list_page()'
        cur_page = response.meta['cur_page']
        cat = response.meta['cat']
        pages_sel = response.xpath('.//div[@id="pagn"]/span')
        try:
            total_page = int(pages_sel.xpath('./text()').extract()[-2])
        except Exception:
            logging.warn('Banned by Amazon at page %d for %c!', cur_page, cat)
            return 
        
        logging.info('Now at %d/%d for %s' % (cur_page, total_page, cat))

        goods_sel = response.xpath('//li[@class="s-result-item  celwidget "]')
        
        ids = goods_sel.xpath('@data-asin').extract()
        names = goods_sel.xpath('.//a[@class="a-link-normal s-access-detail-page  a-text-normal"]/@title').extract()
        urls = goods_sel.xpath('.//a[@class="a-link-normal s-access-detail-page  a-text-normal"]/@href').extract()
        prices = AmazonTools.get_price(goods_sel)
        promotes = AmazonTools.get_promote(goods_sel)
        pics = goods_sel.xpath('.//img[@class="s-access-image cfMarker"]/@src').extract()
        comments = AmazonTools.get_comment(goods_sel)
        histories, stocks = AmazonTools.get_histories_stock(ids)
        
        for i in xrange(len(ids)):
            item = JdItem()
            item['idInMarket'] = ids[i]
            item['name'] = names[i]
            item['url'] = urls[i]
            item['price'] = prices[i]
            item['discount'] = promotes[i]
            item['pics'] = [pics[i]]
            item['comment'] = comments[i]
            item['market'] = 'AMAZON'
            item['updateTime'] = AmazonTools.get_timestamp()
            item['priceChangeHistory'] = histories[i]
            item['stock'] = stocks[i]
            logging.info(item)
#             yield item
        
        # 翻页
        if cur_page < total_page:
            next_page_url = self.goods_list_url_template % pages_sel[-1].xpath('./a/@href').extract()[0]
            yield scrapy.Request(next_page_url,
                                 callback=self.parse_goods_list_page,
                                 meta={'cur_page':cur_page + 1,
                                       'cat':cat})
        else:
            logging.info('Complete crawling %s' % cat)
            
    
        
        
        
        
        
        
