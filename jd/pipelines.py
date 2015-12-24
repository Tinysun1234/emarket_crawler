# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import logging
import settings
import time
from scrapy.exceptions import DropItem
from pymongo.mongo_client import MongoClient

class JdPipeline(object):
    def __init__(self):
        conn = pymongo.MongoClient(settings.MONGODB_SERVER, settings.MONGODB_PORT)
        collection_name = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.collections_dict = {dbname:conn[dbname][collection_name] \
                                 for dbname in settings.MONGODB_DB}

        
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing %s" % data)
        if valid:
            # self.collection.insert(dict(item))
            self.collections_dict[item['market']].insert(dict(item))
            logging.debug("Item added to db:" + item['market'])
        return item

class CloudPipeline(object):
    def __init__(self):
        # conn=MongoClient('mongodb://price:dslab123@139.129.11.74/price')
        self.conn = MongoClient('mongodb://' + settings.MONGODB_DB_CLOUD + ':'\
                         + settings.MONGODB_USER_PASSWD_CLOUD[settings.MONGODB_DB_CLOUD] + '@'\
                         + settings.MONGODB_SERVER_CLOUD + '/' + settings.MONGODB_DB_CLOUD)
        if self.conn:
            logging.debug('connected to cloud mongodb.')
            
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing %s" % data)
        if valid:
            # self.collection.insert(dict(item))
            self.conn[settings.MONGODB_DB_CLOUD]['goodInfo'].insert(dict(item))
            logging.debug("Item from " + item['market'] + 'inserted!')
        return item
