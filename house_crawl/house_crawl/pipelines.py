# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import traceback
import logging
import pymongo
from scrapy import signals
from scrapy.exceptions import NotConfigured, DropItem
from .items import HouseCrawlItem

class HouseCrawlPipeline(object):

    def __init__(self, mongo_uri, mongo_col):
        self.mongo_uri = mongo_uri
        self.mongo_col = mongo_col

    @classmethod
    def from_crawler(cls, crawler):
        '''
        set connection info from settings
        :param crawler:
        :return:
        '''
        if not crawler.settings.getbool('MONGO_EXPORT_ENABLED'):
            logging.warning("MONGO_EXPORT NotConfigured. ")
            raise NotConfigured

        pipeline = cls(
                    mongo_uri=crawler.settings.get('MONGO_URI'),
                    mongo_col=crawler.settings.get('MONGO_COLLECTION')
                    )
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.database = self.client['test'] # default database
        self.collection = self.database[self.mongo_col]

        logging.info("[MONGO EXPORT] mongo uri: %s", self.mongo_uri)
        logging.info("[MONGO EXPORT] mongo colname: %s", self.mongo_col)
        logging.info("[MONGO EXPORT] mongo client: %s", self.client)
        logging.info("[MONGO EXPORT] mongo database: %s", self.database)
        logging.info('[Mongodb Client] collections: %s', self.database.list_collection_names())
        self.create_index()

    def spider_closed(self, spider):
        self.client.close()

    def create_index(self):
        v = {
            'raw_key': {'name': 'raw_key', 'unique': True},
            'url': {'name': 'url'},
            'scraped_time': {'name': 'scraped_time'},
            'district': {'name':'district'}
        }
        for key, kwargs in v.items():
            self.collection.create_index(key, background=True, **kwargs)
        logging.info(self.collection.index_information())

    def process_item(self, item, spider):
        '''
        save item to mongodb
        :param item: define in items.py dict-like
        :param spider:
        :return:
        '''

        # if item['category'] == 'detail':
        #     if 'college' not in item or not item['college']:
        #         raise DropItem("ignore %s" % item)

        if not isinstance(item, HouseCrawlItem):
            return item

        try:
            raw_key = item['raw_key']
            self.collection.update_many({'raw_key': raw_key}, {'$set': dict(item)}, upsert=True)
        except Exception as e:
            logging.fatal('storage error %s, %s', item, e)
            traceback.print_exc()
        return item
