# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    # define the fields for your item here like:
    market = scrapy.Field()  # 网站
    category = scrapy.Field()  # 类别
    name = scrapy.Field()  # 标题
    idInMarket = scrapy.Field()  # 商品ID
    price = scrapy.Field()  # 价格
    comment = scrapy.Field()  # 评论数
    url = scrapy.Field()  # 详情页url
#     image_fname = scrapy.Field()  # 图片路径
    # new 
#     market = scrapy.Field()  # 网站，与site重复
    mobilePrice = scrapy.Field()  # 移动端价格
    discount = scrapy.Field()  # 促销描述
    stock = scrapy.Field()  # 库存
    commonComment = scrapy.Field()  # 标签。应为Tag
    updateTime = scrapy.Field()  # 更新时间
    pics = scrapy.Field()  # 标题图片url
    priceChangeHistory = scrapy.Field()  # 历史价格
    vendor = scrapy.Field()  # 厂家
    shop = scrapy.Field()  # 店铺名
    pass
