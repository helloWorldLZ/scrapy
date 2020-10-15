# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Lottery(scrapy.Item):
    date = scrapy.Field()      #   开奖日期
    issue = scrapy.Field()     #   期号
    red_balls = scrapy.Field()      #   红球号码
    blue_balls = scrapy.Field()     #   蓝球号码
    url = scrapy.Field()


class Product(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    productId = scrapy.Field()
    shopName = scrapy.Field()
    shopUrl = scrapy.Field()

    brand = scrapy.Field()
    parameterList = scrapy.Field()
    tableItem = scrapy.Field()
    packageList = scrapy.Field()

    comments = scrapy.Field()
    imgs = scrapy.Field()
    pageNum = scrapy.Field()

    # image_urls = scrapy.Field()
    # images = scrapy.Field()
