# -*- coding: utf-8 -*-

__author__ = 'BuGoNee'

import logging
import base64
import random

from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class ProxyMiddleware(object):
    """
    A Proxy middleware .
    """

    def __init__(self, settings):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        if not s.getbool('PROXY_ENABLED'):
            logger.info("PROXY NotConfigured. ")
            raise NotConfigured
        middleware = cls(s)
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        pass

    def spider_opened(self, spider):
        proxyHost = "tunnel.kuyukuyu.com"
        proxyPort = "18188"
        # 代理隧道验证信息
        proxyUser = "13115067856"
        proxyPass = "5dc498d1"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": proxyHost, "port": proxyPort, "user": proxyUser,
        "pass": proxyPass, }

        user = proxyUser
        password = proxyPass
        auth = bytes((user + ":" + password), "ascii")
        self.proxyAuth = "Basic " + base64.urlsafe_b64encode(auth).decode("utf8")

        self.proxies = {"http": proxyMeta, "https": proxyMeta, }

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        #  if 'proxy' in request.meta:
            #  return

        if request.meta.get('dont_proxy', False):
            logger.debug('dont_proxy <%s>:<True>' % request)
        else:
            request.meta["proxy"] = self.proxies
            request.headers["Proxy-Authorization"] = self.proxyAuth

    def process_exception(self, request, exception, spider):
        # request.meta['dont_proxy'] = True
        logger.info('proxy exception <%s>:<%s>' % (request, exception))
