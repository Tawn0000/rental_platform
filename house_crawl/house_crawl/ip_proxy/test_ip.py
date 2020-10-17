import json
import requests
from ip_proxy import XiciProxiesSpider
with open("proxies.json",'r', encoding='UTF-8') as f:
    IPPOOL = json.load(f)

# fps = XiciProxiesSpider()
# IPPOOL = fps.run()

def validate_ip(item, ip_type):
    try:
        test_url = "{}://baidu.com".format(ip_type)
        response = requests.get('http://baidu.com', proxies=item, timeout=2)
        print(response.status_code)
        if response.status_code == 200:
            return True
        return False
    except Exception as ex:
        return False

for x in IPPOOL['http']:
    item = {'http':x}
    print(type(item))
    if validate_ip(item, 'http'):
        print("validate: ")
        print(item)
    else:
        print("remove:")
        print(item)

for x in IPPOOL['https']:
    item = {'https':x}
    if validate_ip(item, 'https'):
        print("validate: ")
        print(item)
    else:
        print("remove:")
        print(item)
