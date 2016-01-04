# -*- coding: utf-8 -*-
import scrapy
from jd.items import JdItem
import logging
import jd.settings
import re
# from scrapy.shell import inspect_response
from tools.jdtools import JDTools
from myspiderbase import MySpiderBase

class JdSpider(MySpiderBase):
    name = "jd"
    site_charset = 'gbk'
    allowed_domains = ['jd.com', '3.cn']
    current_page = 1
    allsort_url = r'http://www.jd.com/allSort.aspx'
    list_url_prefix = r'http://list.jd.com'
    price_url_prefix = r'http://p.3.cn/prices/mgets?skuids='
    comment_count_url_prefix = r'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds='
    goods_meta = dict()

    start_urls = (
        allsort_url,
    )

    def parse(self, response):
        return self.get_goods_type_in_allsort_page(response)

    def get_goods_type_in_allsort_page(self, response):
        '''
        生成指定大类型的小类型商品列表页request
        '''
        type_names = jd.settings.GOODS_TYPE_NAMES['jd']
        type_sel_list = []
#         JDTools.detect_charset(response)
        try:
            all_type_sels = response.xpath('//div[@class="category-item m"]')
            for type_sel in all_type_sels:
                this_type_name = type_sel.xpath('./div[@class="mt"]//span/text()').extract()[0].encode('utf8')
                if  this_type_name in type_names:
                    type_sel_list += type_sel.xpath('./div[@class="mc"]//dd//a')
            
            type_title_list = [type_sel.xpath('./text()').extract() for type_sel in type_sel_list]
            type_url_list = [type_sel.xpath('./@href').extract() for type_sel in type_sel_list]
            type_tuple = zip(type_title_list, type_url_list)
            logging.info('%d types in page!' % len(type_sel_list))
        except Exception:
            logging.warn('Goods list page not struct properly!')
#             inspect_response(response, self)
            return
        
        for type_item in type_tuple:
            type_title = type_item[0][0]
            type_url = type_item[1][0]
#             logging.debug('type_title:%s\ttype_url:%s' % (type_title, type_url))
            yield scrapy.Request(type_url,
                                 callback=self.parse_goods_list_page,
                                 meta={'cur_page':1,
                                       'category':type_title,
                                       'page_url_prefix':type_url})
    
    def parse_goods_list_page(self, response): 
        '''
        解析商品列表页，生成各商品详情页request
        '''
        category = response.meta['category'] 
        cur_page = response.meta['cur_page']   
        page_url_prefix = response.meta['page_url_prefix']
        total_page = int(response.xpath('//span[@class="fp-text"]/i/text()').extract()[0])
        # 获取当前页面所有商品链接并生成request_list
        glist = response.xpath('//div[@id="plist"]/ul/li')        
        detail_urls = [ raw_link for raw_link in glist.xpath('.//div[@class="p-name"]/a/@href').extract()]
#         shops = [ JDTools.convert_to_utf8(vendor) \
#                  for vendor in response.xpath('//div[@class="p-shop"]/@data-shop_name').extract()]
#         id_list = glist.xpath('.//div[@data-sku]/@data-sku').extract()
        # 当前页面无商品
        if not detail_urls:
            logging.info('No goods for %s at page %d/%d!' % (category, cur_page, total_page))
            return 
        
        try:
            total_page = int(response.xpath('//span[@class="fp-text"]/i/text()').extract()[0])
        except Exception as e:
            logging.debug(e)
            return
        logging.info('Now at page %d/%d for %s' % (cur_page, total_page , category))
       
        for i, detail_url in enumerate(detail_urls):
            item = JdItem()
            item['category'] = category
#             item['shop'] = shops[i]
            yield scrapy.Request(detail_url,
                                 callback=self.parse_detail_page,
                                 meta={'item':item})           

        # 生成下一页的request
        if cur_page < total_page:
            nextpage_url = page_url_prefix + '&page=' + str(cur_page + 1)
            yield scrapy.Request(nextpage_url,
                                 callback=self.parse_goods_list_page,
                                 meta={'category':category,
                                       'cur_page':(cur_page + 1),
                                       'page_url_prefix':page_url_prefix})  
        else:
            logging.info('Complete crawling %s' % category)

    def parse_detail_page(self, response):
        '''
        解析商品详情页
        '''
        try:
            goods_info_sel = response.xpath('//div[@id="p-box"]')
            self.get_goodsmeta(response)
            logging.debug(self.goods_meta)
        
        except Exception:
            logging.warn('Detail page struct not properly!')
            return

        item = response.meta['item']

        item['url'] = self.goods_meta['url']
        item['idInMarket'] = self.get_id()
        item['name'] = self.get_name(goods_info_sel)
        item['price'] = JDTools.get_price(self.goods_meta)
        item['discount'] = JDTools.get_promotion(self.goods_meta)
        item['comment'] = JDTools.get_comment(self.goods_meta)
        item['market'] = self.goods_meta['market']
        item['updateTime'] = JDTools.get_timestamp()
        item['commonComment'] = JDTools.get_tags(self.goods_meta)
        item['stock'] = JDTools.get_stock(self.goods_meta)
        item['pics'] = JDTools.get_pics(goods_info_sel)
        item['priceChangeHistory'] = JDTools.get_history_price(self.goods_meta)
        item['shop'] = JDTools.get_shop(response)

#            inspect_response(response, self)
        return item
#         if JDTools.convert_to_utf8(item['shop']) != JDTools.convert_to_utf8('京东自营'):
#             print item['shop']

    
    def get_goodsmeta(self, response):
        self.goods_meta['skuId'] = re.search(r'skuid\s*:\s*(\d+)', response.body).group(1)
        self.goods_meta['shopId'] = re.search(r"shopId\s*:\s*'(\d+)'", response.body).group(1)
        self.goods_meta['venderId'] = re.search(r"venderId\s*:\s*(\d+)", response.body).group(1)
        self.goods_meta['cat'] = re.search(r'cat\s*:\s*\[([0-9,]+)\]', response.body).group(1)
        self.goods_meta['url'] = response.url
        self.goods_meta['market'] = 'JD'
                
    def get_id(self):
        return re.search(r'(\d+)\.htm', self.goods_meta['url']).group(1)
        
    def get_name(self, goods_info_sel):
        return JDTools.convert_to_utf8(goods_info_sel.xpath('//div[@id="name"]/h1/text()')[0].extract())     
        
