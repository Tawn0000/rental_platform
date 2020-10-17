# -*- coding: utf-8 -*-
import datetime
import random
import scrapy
from pymongo import MongoClient
from bs4 import BeautifulSoup
from house_crawl.items import HouseCrawlItem
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class FangDetailsSpider(scrapy.Spider):
    name = 'fang_details'
    custom_settings = {
    'URLLENGTH_LIMIT': 100000,
    'DOWNLOAD_DELAY': 0.2,
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
        'house_crawl.deltafetch.DeltaFetchMiddleware': 543,
    },
    'DELTAFETCH_ENABLED': True,
    'DELTAFETCH_KEY_NAME': 'raw_key',
    'DELTAFETCH_DB_NAME': 'test',
    'DELTAFETCH_COLLECTION_NAME': 'fang_details_crawl',
    'DELTAFETCH_TYPE': 'MONGO',

    'ITEM_PIPELINES': {
        'house_crawl.pipelines.HouseCrawlPipeline': 300,
    },
    'MONGO_EXPORT_ENABLED': True,
    'MONGO_COLLECTION': 'fang_details_crawl',
    'MONGO_COLLECTION_LIST': 'fang_list_crawl_new',
    'COOKIES_ENABLED': True,
    'COOKIES_DEBUG': False,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    'CONCURRENT_REQUESTS_PER_IP': 8,
    }
    url_pre = 'https://sh.zu.fang.com'
    Debug = False

    def start_requests(self):
        self.client = MongoClient(self.settings['MONGO_URI'])
        self.database = self.client['test']
        self.collection = self.database[self.settings['MONGO_COLLECTION_LIST']]
        tag = ['浦东','嘉定','宝山','闵行','松江','普陀','静安','黄浦','虹口','青浦','奉贤','金山','杨浦','徐汇','长宁','崇明','上海周边']
        st = 0
        num = 100
        if self.Debug:
            url = 'https://sh.zu.fang.com/chuzu/3_375729079_1.htm'
            req = scrapy.Request(url=url, cookies=self.cookies, callback=self.parse_redirect, dont_filter=True)
            req.meta['info'] = {"district":'浦东', "url":url}
            req.meta['priority'] = 100
            req.meta['deltafetch_key'] = url
            yield req
        else:
            for dis in tag:
            # dis = tag[16]
                cur = self.collection.find({"district":dis}).skip(st).limit(num)
                for item in cur:
                    soup = BeautifulSoup(item['html'], features="lxml")
                    tmp = soup.find_all(name="p", attrs={"class":"title"})
                    for it in tmp:
                        url = self.url_pre + it.find('a')['href']
                        # print("url: " + url)
                        req = scrapy.Request(url=url, cookies=self.cookies, callback=self.parse_redirect, dont_filter=True)
                        req.meta['deltafetch_key'] = url
                        req.meta['info'] = {"district":dis, "url":url}
                        req.meta['priority'] = 100
                        req.meta['deltafetch_key'] = url
                        yield req

    def parse_redirect(self, response):
        url_direct = response.xpath("//*[@class='btn-redir']/@href").get()
        if not url_direct:
            # with open("index.html",'w') as f:
            #     f.write(response.text)
            # self.crawler.engine.close_spider(self, response.url)
            return self.parse(response)

        else:
            # print("%%%%%%%%")
            # print("re_url: " + url_direct)
            # print("%%%%%%%%")
            return self.req_details(url=url_direct, info=response.meta['info'])

    def req_details(self, url, info):
        req = scrapy.Request(url=url, cookies=self.cookies, callback=self.parse, dont_filter=True)
        req.meta['info'] = info
        req.meta['deltafetch_key'] = info['url']
        req.meta['priority'] = 200
        yield req

    def parse(self, response):
        # print("*******")
        # print(response.url)
        # print("*******")
        # with open("index.html",'w') as f:
            # f.write(response.text)
        if response.url.find('captcha') != -1:
            print("^^^^^^^^^")
            # self.crawler.engine.close_spider(self, '302: captcha')
        else:
            item = HouseCrawlItem()
            item['raw_key'] = response.meta['info']['url']  # 被爬取网站的主键
            item['domain'] = 'sh.zu.fang.com'  # 被爬网站的标识
            item['url'] = response.url  # 爬取url
            item['category'] = 'details'  # 页面类别,列表页or详情页
            item['html'] = response.text
            item['district'] = response.meta['info']['district']
            item['scraped_time'] = str(datetime.datetime.now())
            # print(item['html'])
            yield item
            # return None


    cookies ={
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
