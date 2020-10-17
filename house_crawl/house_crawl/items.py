# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HouseCrawlItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    raw_key = Field() # 被爬取网站的主键
    domain = Field() # 被爬网站的标识
    url = Field() # 爬取url
    category = Field()  # 页面类别,列表页or详情页
    html = Field()
    district = Field()
    scraped_time = Field()

    def __repr__(self):
        """only print out summary after exiting the Pipeline"""
        return repr({
            "summary": "{} on {}".format(self['url'], self['category'])
        })
