# -*- coding: utf-8 -*-

__author__ = 'BuGoNee'

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import Request
from scrapy.item import BaseItem
import logging
logger = logging.getLogger(__name__)


class DeltaFetchMiddleware(object):
    """
    This is a spider middleware to ignore requests to pages containing items
    seen in previous crawls of the same spider, thus producing a "delta crawl"
    containing only new items.

    This also speeds up the crawl, by reducing the number of requests that need
    to be crawled, and processed (typically, item requests are the most cpu
    intensive).
    """
    def __init__(self, settings, stats=None):
        self.stats = stats
        self.deltafetch_type = settings.get('DELTAFETCH_TYPE', '')

        self.DELTAFETCH_KEY_NAME = settings.get('DELTAFETCH_KEY_NAME')
        self.DELTAFETCH_DB_NAME = settings.get('DELTAFETCH_DB_NAME')
        if self.deltafetch_type == 'MONGO':
            self.DELTAFETCH_COLLECTION_NAME = settings.get('DELTAFETCH_COLLECTION_NAME')
            from pymongo import MongoClient
            client = MongoClient(settings['MONGO_URI'])
            database = client[self.DELTAFETCH_DB_NAME]
            self.db = database[self.DELTAFETCH_COLLECTION_NAME]

        else:
            logger.error("UNKNOWN DELTAFETCH_TYPE. %s", self.deltafetch_type)
        logger.info("[DELTAFETCH INIT] TYPE: %s." % self.deltafetch_type)
        logger.info("[DELTAFETCH INIT] KEY_NAME: %s." % self.DELTAFETCH_KEY_NAME)
        logger.info("[DELTAFETCH INIT] DB_NAME: %s." % self.DELTAFETCH_DB_NAME)
        logger.info("[DELTAFETCH INIT] stats: %s." % self.stats)

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        if not s.getbool('DELTAFETCH_ENABLED'):
            logger.info("DELTAFETCH NotConfigured. ")
            raise NotConfigured
        middleware = cls(s, crawler.stats)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        if self.deltafetch_type == 'MySQL':
            self.db.close()

    def spider_opened(self, spider):
        pass

    # start_requests 发出的requests
    def process_start_requests(self, start_requests, spider):
        pairs = dict()
        # print("*********")
        # print(start_requests)
        # print(type(start_requests))
        # print("*********")
        for r in start_requests:
            if isinstance(r, Request):
                key = self._get_key(r)
                if key:
                    pairs[key] = r
                    continue
        yield r
        keys = pairs.keys()
        # print("&&&&&&&&")
        # print(keys)
        # print("&&&&&&&")
        key_name = self.DELTAFETCH_KEY_NAME
        keys = [str(k) for k in keys]
        cur = self.db.find({key_name: {'$in': keys}}, {key_name: 1, '_id': 0})
        # print("&&&&&&&&")
        # print(list(cur))
        # print("&&&&&&&")
        exists_keys = list(cur) if keys else []
        exists_keys = [str(e.get(self.DELTAFETCH_KEY_NAME)) for e in exists_keys]
        # print("&&&&&&&&")
        # print(exists_keys)
        # print("&&&&&&&")
        logger.debug("EXISTS KEYS IN DB: %s" % exists_keys)
        for key, r in pairs.items():
            if key in exists_keys:
                logger.debug("Ignoring already visited: %s,%s" % (key, r))
                if self.stats:
                    self.stats.inc_value('deltafetch/skipped', spider=spider)
            else:
                # print("***")
                # print(r.url)
                # print("***")
                yield r

    def process_spider_output(self, response, result, spider):
        pairs = dict()
        for r in result:
            if isinstance(r, Request):
                key = self._get_key(r)
                if key:
                    pairs[key] = r
                    continue
            elif isinstance(r, (BaseItem, dict)):
                key = self._get_key(response.request)
                if self.stats:
                    self.stats.inc_value('deltafetch/stored', spider=spider)
            yield r
        keys = pairs.keys()
        # print(keys)
        key_name = self.DELTAFETCH_KEY_NAME
        keys = [str(k) for k in keys]
        cur = self.db.find({key_name: {'$in': keys}}, {key_name: 1, '_id': 0})
        exists_keys = list(cur) if keys else []
        # print(exists_keys)
        exists_keys = [str(e.get(self.DELTAFETCH_KEY_NAME)) for e in exists_keys]
        logger.debug("EXISTS KEYS IN DB: %s" % exists_keys)
        for key, r in pairs.items():
            if key in exists_keys:
                logger.debug("Ignoring already visited: %s,%s" % (key, r))
                if self.stats:
                    self.stats.inc_value('deltafetch/skipped', spider=spider)
            else:
                yield r

    def _get_key(self, request):
        # print(request.meta)
        key = request.meta.get('deltafetch_key', '')
        return key


if __name__ == '__main__':
    pass
