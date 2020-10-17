# -*- coding: utf-8 -*-
import datetime
import random
import re
import os
import base64
import urllib
import scrapy
import urllib.parse
from io import BytesIO
from bs4 import BeautifulSoup
from scrapy.http import Request,FormRequest
from fake_useragent import UserAgent
from house_crawl.items import HouseCrawlItem
from scrapy.utils.project import get_project_settings


settings = get_project_settings()


class FangListSpider(scrapy.Spider):
    name = 'fang_list'
    allowed_domains = ['sh.zu.fang.com','manfen5.com', 'exercise.kingname.info', 'whatismybrowser.com']
    # start_urls = ['https://sh.zu.fang.com/']

    custom_settings = {
        'URLLENGTH_LIMIT': 100000,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 8,
        'TELNETCONSOLE_PORT': [],
        'REDIRECT_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [429, 503, 502],
        'DEFAULT_REQUEST_HEADERS': {},
        'DOWNLOADER_MIDDLEWARES': {
            'house_crawl.middlewares.RandomUserAgent': 1,
            # 'house_crawl.middlewares.ProxyMiddleware': 902,
            # 'house_crawl.dailiyun.ProxyMiddleware': 902,
        },
        'USER_AGENT_ROTATE_ENABLED': True,
        'USER_AGENT_TYPE': 'PC',
        'PROXY_ENABLED': False,

        'SPIDER_MIDDLEWARES': {
            'house_crawl.deltafetch.DeltaFetchMiddleware': 901,
        },
        'DELTAFETCH_ENABLED': True,
        'DELTAFETCH_KEY_NAME': 'raw_key',
        'DELTAFETCH_DB_NAME': 'test',
        'DELTAFETCH_COLLECTION_NAME': 'fang_list_crawl_new',
        'DELTAFETCH_TYPE': 'MONGO',

        'ITEM_PIPELINES': {
            'house_crawl.pipelines.HouseCrawlPipeline': 300,
        },
        'MONGO_EXPORT_ENABLED': True,
        'MONGO_COLLECTION': 'fang_list_crawl_new',
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'CONCURRENT_REQUESTS_PER_IP': 4,
    }

    DEBUG = False
    # 实例化一个cookiejar对象
    url_pre = 'https://sh.zu.fang.com'
    # url_pre = 'http://exercise.kingname.info/exercise_middleware_ua/1'
    # url_pre = 'https://sh.zu.fang.com/chuzu/3_374394576_1.htm'
    # url_pre = 'http://search.fang.com/captcha-af8a96099589a74747/redirect?h=https://sh.zu.fang.com/chuzu/3_374394576_1.htm'
    def parse_test(self, response):
        with open("index.html",'w') as f:
            f.write(response.text)
        return None

    def start_requests(self):
        return self.req_index()

    def req_index(self):
        req = scrapy.Request(url=self.url_pre, callback=self.parse_index, dont_filter=True)
        yield req

    def parse_index(self, response):
        tmp  = response.xpath('//*[@id="rentid_D04_01"]/dd').get()
        soup = BeautifulSoup(tmp, features="lxml")
        district_url = {}
        for pos in soup.find_all('a'):
            if(pos.string == '不限'):
                continue
            else:
                url = self.url_pre + pos.get('href')
                district_url[pos.string] = url
                if(self.DEBUG):
                    break
        print(district_url)
        # return None
        return self.req_district(district_url)

    def req_district(self, district_url, headers=None):
        tag = ['浦东','嘉定','宝山','闵行','松江','普陀','静安','黄浦','虹口','青浦','奉贤','金山','杨浦','徐汇','长宁','崇明','上海周边']
        for (k,v) in district_url.items():
            # if(k == tag[16]):
                # v = 'https://sh.zu.fang.com/house-a029/i390/'
            req = scrapy.Request(url=v, cookies=self.cookies, callback=self.parse, dont_filter=True)
            req.meta['district'] = k
            # req.meta['deltafetch_key'] = v
            yield req

    def parse(self, response):
        if response.url.find('captcha') != -1:
            print("^^^^^^^^^")
            self.crawler.engine.close_spider(self, '302: captcha')
        item = HouseCrawlItem()
        item['raw_key'] = response.url  # 被爬取网站的主键
        item['domain'] = 'sh.zu.fang.com'  # 被爬网站的标识
        item['url'] = response.url  # 爬取url
        item['category'] = 'list'  # 页面类别,列表页or详情页
        item['html'] = response.text
        item['district'] = response.meta['district']
        item['scraped_time'] = str(datetime.datetime.now())
        yield item
        tmp1 = response.xpath('//*[@id="rentid_D10_01"]/a[7]/@href').get()
        txt1 = response.xpath('//*[@id="rentid_D10_01"]/a[7]/text()').get()
        tmp2 = response.xpath('//*[@id="rentid_D10_01"]/a[8]/@href').get()
        txt2 = response.xpath('//*[@id="rentid_D10_01"]/a[8]/text()').get()

        tmp = None
        if txt1 == '下一页':
            tmp = tmp1
        if txt2 == '下一页':
            tmp = tmp2

        if tmp:
            req = scrapy.Request(url=self.url_pre+tmp, cookies=self.cookies, callback=self.parse, dont_filter=True)
            req.meta['district'] = response.meta['district']
            yield req

    cookies = {
    "global_cookie":"j7qqhvn9ffthnrtw0r2qdieyp1ck7e63hlo",
    "integratecover":"1",
    "__utmc":"147393320",
    "Rent_StatLog":"0f47ec14-0b20-481d-b94c-826085f68b04",
    "Integrateactivity":"notincludemc",
    "lastscanpage":"0",
    "city":"sh",
    "__utma":"147393320.905361585.1583377535.1585371301.1585377844.48",
    "__utmz":"147393320.1585377844.48.41.utmcsr=sh.fang.com|utmccn=(referral)|utmcmd=referral|utmcct=/",
    "__utmt_t0":"1",
    "__utmt_t1":"1",
    "__utmt_t2":"1",
    "keyWord_recenthousesh":"%5b%7b%22name%22%3a%22%e6%b5%a6%e4%b8%9c%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a025%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e5%98%89%e5%ae%9a%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a029%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e9%9d%92%e6%b5%a6%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a031%2f%22%2c%22sort%22%3a1%7d%5d",
    "Captcha":"3757626C4C79466C615974625A5A446C6162674D4452636578346B475364694C6A723074744E58432F6B674352352F4F7A6D4259694F2B454846646C616E525A4F4B2B45496C744A4378493D",
    "g_sourcepage":"zf_fy%5Exq_pc",
    "__utmb":"147393320.21.10.1585377844",
    "unique_cookie":"U_xxg4h31hd7q4tskvaoablegkv2lk7u7i5r7*34"
}
