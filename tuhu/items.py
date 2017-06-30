# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TuhuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    shoplevel = scrapy.Field()
    shophours = scrapy.Field()
    shoptype = scrapy.Field()
    paymenttype = scrapy.Field()
    tel = scrapy.Field()
    addr = scrapy.Field()
    tireservice_yes = scrapy.Field()
    tireservice_no = scrapy.Field()
    maintenance_yes = scrapy.Field()
    maintenance_no = scrapy.Field()
