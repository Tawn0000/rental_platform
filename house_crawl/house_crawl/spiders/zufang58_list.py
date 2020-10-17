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


class Zufang58ListSpider(scrapy.Spider):
    name = 'zufang58_list'
    allowed_domains = ['sh.58.com/zufang']
    start_urls = ['https://sh.58.com/zufang']

    custom_settings = {
        'URLLENGTH_LIMIT': 100000,
        'DOWNLOAD_DELAY': 1,
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
        'DELTAFETCH_COLLECTION_NAME': 'zufang58_list_crawl',
        'DELTAFETCH_TYPE': 'MONGO',

        'ITEM_PIPELINES': {
            'house_crawl.pipelines.HouseCrawlPipeline': 300,
        },
        'MONGO_EXPORT_ENABLED': True,
        'MONGO_COLLECTION': 'zufang58_list_crawl',
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    DEBUG = False
    # 实例化一个cookiejar对象
    url_pre = 'https://sh.58.com/chuzu'
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
        soup = BeautifulSoup(response.text, features="lxml")
        tmp = soup.find(name="dl", attrs={"class":"secitem secitem_fist"})
        district_url = {}
        for pos in tmp.find_all('a'):
            if(pos.string == '不限'):
                continue
            else:
                url =  pos.get('href')
                district_url[pos.string] = url

        print(district_url)
        # return None
        return self.req_district(district_url)

    def req_district(self, district_url, headers=None):
        tag = ['浦东','嘉定','宝山','闵行','松江','普陀','静安','黄浦','虹口','青浦','奉贤','金山','杨浦','徐汇','长宁','崇明','上海周边']
        for (k,v) in district_url.items():
            # if(k == tag[16]):
            req = scrapy.Request(url=v, cookies=self.cookies, callback=self.parse, dont_filter=True)
            req.meta['district'] = k
            yield req

    def parse(self, response):
        item = HouseCrawlItem()
        item['raw_key'] = response.url  # 被爬取网站的主键
        item['domain'] = 'sh.58.com'  # 被爬网站的标识
        item['url'] = response.url  # 爬取url
        item['category'] = 'list'  # 页面类别,列表页or详情页
        item['html'] = response.text
        item['district'] = response.meta['district']
        item['scraped_time'] = str(datetime.datetime.now())
        # print("********")
        # print(item)
        # return None
        yield item

        soup = BeautifulSoup(response.text, features='lxml')
        next = soup.find(name='a',attrs={"class":"next"})
        if next:
            tmp = next.get('href', '')
            txt = next.string
        # print(tmp)
        # print(txt)
            req = scrapy.Request(url=tmp, cookies=self.cookies, callback=self.parse, dont_filter=True)
            req.meta['district'] = response.meta['district']
            yield req

    cookies = {
    "f":"n",
    "userid360_xml":"5CD04D81900502C19C0C50A1A1FE1749",
    "time_create":"1587261748515",
    "commontopbar_new_city_info":"2%7C%E4%B8%8A%E6%B5%B7%7Csh",
    "commontopbar_ipcity":"zhuzhou%7C%E6%A0%AA%E6%B4%B2%7C0",
    "myLat":"\"\"",
    "myLon":"\"\"",
    "id58":"+1h++l50JARRQvbONbaVwQ==",
    "mcity":"su",
    "58home":"su",
    "58tj_uuid":"07d7283d-d899-4275-a51b-97809cb68727",
    "als":"0",
    "wmda_uuid":"31ba44231fffab18114db017c6593d5f",
    "wmda_new_uuid":"1",
    "xxzl_cid":"8790d4faec034e6a8ff26bf55a85dbd5",
    "xzuid":"44e55b8f-485e-4d8d-8644-b29b556de492",
    "xxzl_deviceid":"Rv7oh%2BG9NZCoi4MMGLeNgUcajl1%2FZQRi%2Fhwdmru7LDoZjTyfheuoYowyXbWTh96b",
    "new_uv":"2",
    "new_session":"0",
    "wmda_session_id_11187958619315":"1584863149478-a4898989-7e03-566e",
    "city":"bj",
    "utm_source":"",
    "spm":"",
    "init_refer":"https%253A%252F%252Fwww.baidu.com%252Flink%253Furl%253D3vUl2pXpDjb0fXub-5XAEH_DPSrh6TsFAwPUjni5P9rZXAd7gMW8JZJ-f1KfBCSh%2526wd%253D%2526eqid%253D82dfbc9b00005833000000055e77178b",
    "ipcity":"cs%7C%u957F%u6C99",
    "myfeet_tooltip":"end",
    "Hm_lvt_3f405f7f26b8855bc0fd96b1ae92db7e":"1584864588",
    "Hm_lpvt_3f405f7f26b8855bc0fd96b1ae92db7e":"1584864588",
    "ppStore_fingerprint":"9333253B9E17FF6518E4597701CAA362AE839E8434C7316E%EF%BC%BF1584864646762",
    "xzfzqtoken":"mgm0dZ%2FpR1u07H%2Ff2%2FtauZVyMcVIK7%2FUmhgA1ja4dKlICraejdBToqpLbscJoXUBin35brBb%2F%2FeSODvMgkQULA%3D%3D",
    "wmda_session_id_2385390625025":"1584866734252-9da4e2f5-df9c-0aa2",
    "wmda_visited_projects":"%3B11187958619315%3B2385390625025"
}
