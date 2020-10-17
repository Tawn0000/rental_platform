import requests
from lxml import etree
import json

class XiciProxiesSpider(object):

    def __init__(self):
        self.start_url = 'http://www.xicidaili.com/nn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
        }

    def get_page_from_url(self, url):
        response = requests.get(url,headers=self.headers)
        return response.content.decode()

    def get_data_from_page(self, page):
        # print(page)
        # 把page转换为Element对象
        html = etree.HTML(page)
        # 获取包含代理信息的tr列表
        trs = html.xpath('//*[@id="ip_list"]/tr')[1:]

        # 遍历trs, 获取数据信息

        data = {
            'http':[],
            'https':[]
        }

        for tr in trs:
            try:
                ip = tr.xpath('./td[2]/text()')[0]
                port = tr.xpath('./td[3]/text()')[0]
                ip_type = tr.xpath('./td[6]/text()')[0].lower()
                # 如果ip不是http或https直接返回
                if ip_type not in data.keys():
                    return
                # 构建代理数据
                item = {ip_type: '{}://{}:{}'.format(ip_type, ip, port)}
                # 检查代理IP是否可用, 如果可用添加到列表中
                if self.validate_ip(item, ip_type):
                #     # print(item)
                    data[ip_type].append(item[ip_type])
            except Exception as ex:
                print(ex)
                print(etree.tostring(tr))

        print(data)
        return data

    def validate_ip(self, item, ip_type):
        try:
            test_url = "{}://baidu.com".format(ip_type)
            response = requests.get(test_url, proxies=item, timeout=2)
            if response.status_code == 200:
                print(item)
                return True
            return False
        except Exception as ex:
            return False

    def save_data(self, data):
        with open('proxies.json', 'w') as f:
            json.dump(data, f, indent=2)


    def run(self):
        data = {
                'http':[],
                'https':[]
            }
        # 获取页面内宽容
        for i in range(1, 10):
            page = self.get_page_from_url(self.start_url + '/' + str(i))
            # 获取可用代理IP
            data_t = self.get_data_from_page(page)
            data['http'] += data_t['http']
            data['https'] += data_t['https']

        # 保存数据
        self.save_data(data)
        return data

if __name__ == '__main__':
    fps = XiciProxiesSpider()
    fps.run()
