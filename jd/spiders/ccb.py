# -*- coding: utf-8 -*-

import scrapy
from myspiderbase import MySpiderBase
from jd.items import JdItem
import logging
import re
import jd.settings
from tools.ccbtools import CcbTools

class CcbSpider(MySpiderBase):
    name = "ccb"
    allowed_domains = ["ccb.com"]
    list_url_prefix = r'http://shop.ccb.com'
    start_urls = (
        r'http://shop.ccb.com/category.jhtml',
    )

    def parse(self, response):
        return self.get_goods_type_in_allsort_page(response)
    
    def get_goods_type_in_allsort_page(self, response):
        '''
        获取商品小类别列表
        '''
        type_names = jd.settings.GOODS_TYPE_NAMES['ccb']
        req_list = []
        major_cat_sels = response.xpath('//div[@class="sorts2"]/dl')
        for major in major_cat_sels:
            cur_cat_name = major.xpath('.//dt[@class="yh"]/a/text()').extract()[0].encode('utf8')
            if cur_cat_name.strip() in type_names:
                minor_cat_sels = major.xpath('.//span/a')
                for minor in minor_cat_sels:
                    minor_names = [minor_name for minor_name in minor.xpath('./text()').extract()]
                    minor_urls = [self.list_url_prefix + minor_url for minor_url in minor.xpath('./@href').extract()]
                
                    func_request = lambda x, y: scrapy.Request(x,
                                                           callback=self.parse_goods_list_page,
                                                           meta={'cat':y, 'cur_page':1})
                    req_list += map(func_request, minor_urls, minor_names)
        
        return req_list

    def parse_goods_list_page(self, response):
        '''
        解析商品列表页
        '''
        cur_page = response.meta['cur_page']
        cat = response.meta['cat']
        
        pro_sel_list = response.xpath('//div[@class="prolist"]/dl')
        # 当前页面无商品
        if not pro_sel_list:
            logging.info('Complete crawling %s' % cat)
            return
        
        try:
            total_page = int(response.xpath('.//div[@class="page"]/big/text()').extract()[0])
            logging.info('cat:%s now at page:%d/%d' % (cat, cur_page, total_page))
        except Exception:
            logging.info('Interpret crawling %s' % cat)
            return
        
        for pro_sel in pro_sel_list:
            try:
                item = JdItem()
                item['category'] = cat
                item['name'] = pro_sel.xpath('.//li[@class="prodname"]/a/@title').extract()[0].encode('utf8')
                item['market'] = 'CCB'
                id_str = pro_sel.xpath('.//li[@class="prodname"]/@id').extract()[0].encode('utf8')
                item['idInMarket'] = re.search(r'\d+', id_str).group(0).encode('utf8')
                item['price'] = CcbTools.str2price(pro_sel.xpath('.//del/text()').extract()[0])
                item['comment'] = int(pro_sel.xpath('.//span[@class="saleout"]/big/text()').extract()[0])
                item['url'] = pro_sel.xpath('.//li[@class="prodname"]/a/@href').extract()[0]
                discount = pro_sel.xpath('.//li/strong/text()').extract()
                if discount:
                    item['discount'] = discount[0].encode('utf8')
                item['updateTime'] = CcbTools.get_timestamp()
                item['pics'] = pro_sel.xpath('.//img[@class="bigimg"]/@src').extract()
                item['shop'] = pro_sel.xpath('.//li')[-2].xpath('./a/text()').extract()[0].encode('utf8')
                yield item
            except Exception as e:
                logging.warn('Fail get proitem for %s due to %s' % (item['idInMarket'], str(e)))
                
        # 翻页
        if cur_page < total_page:
            cur_page_url = response.url
            
            if cur_page == 1:
                cur_page += 1
                next_page_url = re.sub(r'\.jhtml', '_%d.jhtml' % (cur_page), cur_page_url)
            else:
                cur_page += 1
                next_page_url = re.sub(r'\d+\.jhtml', '%d.jhtml' % (cur_page), cur_page_url)
                
#             logging.info('nextpage url:%s' % next_page_url)
            yield scrapy.Request(next_page_url,
                                 callback=self.parse_goods_list_page,
                                 meta={'cur_page':cur_page,
                                       'cat':cat})
        else:
            logging.info('Complete crawling %s' % cat)
        
        
        
        
        
        
