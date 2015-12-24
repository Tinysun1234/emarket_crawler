# -*- coding: utf-8 -*-
import scrapy
import jd.settings
import time
import os
import hashlib
import logging


class MySpiderBase(scrapy.Spider):
    
    def __init__(self):
        pass
#         self.file_path()
    def file_path(self):
        '''
        设置图片存储路径
        '''
        image_path = jd.settings.TOP_PATH + 'db_image/' + self.name + '/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '/'
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        self.image_path = image_path
        self.image_path_relate = 'db_image/' + self.name + '/' + time.strftime('%Y%m%d', time.localtime(time.time())) + '/'
    
    def get_goods_type_in_allsort_page(self, response):
        pass
    
    def parse_goods_list_page(self, response):
        pass
    
    def parse_detail_page(self, response):
        pass
    
    
    def parse_imageurl(self, response):
        '''
        保存标题图片，并设置图片路径
        '''
        item = response.meta['item']
        item['pics'] = response.url
#         item['image_fname'] = self.image_path_relate + hashlib.sha1(response.url).hexdigest()
        self.set_common_values(item)
    
    def set_common_values(self, item):
        item['updateTime'] = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time()))
        return item
    
    def save_image_to_file(self, response):
        image_file = self.image_path + hashlib.sha1(response.url).hexdigest()
        try:
            f = open(image_file, 'wb')
            f.write(response.body)
            f.close()
            return True
        except Exception as e:
            logging.warn('Store image %s failed! Err: %s' % (response.url, e))
            return False
