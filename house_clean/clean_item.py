import re
import math
import settings
import stations_information
import hashlib
import logging
import requests
from pymongo import MongoClient, UpdateOne
import multiprocessing
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def _hash(data):
    md5 = hashlib.md5() # 应用MD5算法
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()

from fontTools.ttLib import TTFont
import base64
import re
import io


def getKey(script):
    try:
        return re.findall(r"base64,(.*)'\).format", script)[0]
    except:
        return None


def getFont(key):
    data = base64.b64decode(key)
    fonts = TTFont(io.BytesIO(data))
    return fonts.getBestCmap()


def getDigit(str):
    d = re.findall(r'(\d+)', str)[0]
    return int(d) - 1


def getRealValue(script, string):
    key = getKey(script)
#     print(key)
    fontMap = getFont(key)
    newMap = dict()
    #微软雅黑的对应的编码
    font58 = {
        '閏': '0x958f',
        '鸺': '0x9e3a',
        '麣': '0x9ea3',
        '餼': '0x993c',
        '鑶': '0x9476',
        '龤': '0x9fa4',
        '齤': '0x9f64',
        '龥': '0x9fa5',
        '龒': '0x9f92',
        '驋': '0x9a4b',
    }
    for key in fontMap.keys():
        value = getDigit(fontMap[key])
        key = hex(key)
        newMap[key] = value
    result = ''
    for char in string:
        temp = font58[char]
        value = newMap[temp]
        result = '%s%d' % (result, value)
    return result

def decode(script, price_str):
    try:
        res = '.'.join([getRealValue(script, it) for it in price_str.split('.')])
    except Exception as e:
        res = price_str
#         print(res)
    return res


def get_coordinate(keywords, city='无锡'):
    url = 'https://restapi.amap.com/v3/assistant/inputtips?output=json&city=%s&keywords=%s&key=%s'
    url = url % (city, keywords, settings.key)
#     print(url)
    response = requests.get(url)
    answer = response.json()
#     print(answer)
    if answer.get('status') == '1' and answer.get('count') != '0':
#         print(answer.get('tips')[0].get('name'))
        res = answer.get('tips')[0].get('location')
        return res if res else None
    else:
        return None
    
    
def get_distance(origin_list, destination):
#     print(destination)
    if not origin_list or not destination:
        return [1000000000 for i in range(len(origin_list))]
    url = 'https://restapi.amap.com/v3/distance?origins=%s&destination=%s&output=json&key=%s'
    origin_str = '|'.join(origin_list)
    url = url % (origin_str, destination, settings.key)
    response = requests.get(url)
    answer = response.json()
#     print(url)
#     print(answer)
    if answer.get('status') == '1':
        return [int(item['distance']) if item else 1000000000 for item in answer.get('results')]
    else:
        return [1000000000 for i in range(len(origin_list))]


def get_traffic(coordinate):
    station_coordinate = stations_information.station_coordinate
#     coordinate = '116.310905,39.992806'
    station_list = [station for station in station_coordinate.keys()]
    # len(station_list)
    station_coordinate_list = []
    distance_list = []
    for (i, station) in enumerate(station_list):
        station_coordinate_list.append(station_coordinate[station])
        if (i+1) % 100 == 0 or i+1 == len(station_list):
            distance_list += get_distance(station_coordinate_list, coordinate)
#             print(len(station_coordinate_list))
            station_coordinate_list = []

    if distance_list.count(None) == len(distance_list):
        return None
    else:
        min_distance = min(distance_list)
        min_index = distance_list.index(min_distance)
        min_station = station_list[min_index]

        if min_station != None and min_distance <= 2000:
            res = '距' + stations_information.station_subway[min_station] + min_station + '地铁站' + str(min_distance) + '米'
        else:
            res = None
        return res

        print(station_list)
        print(distance_list)
        print(min_distance)
        print(min_index)
        print(min_station)
        print(res)

# coordinate = '121.192279,31.171247'
# get_traffic(coordinate)
    

def worker_1(st, num):
#     print("*")
    # 注意父子进程不能共用同一MongoDB connection
    MONGO_COLLECTION_1 = 'fang_details_crawl'
    MONGO_COLLECTION_OUTPUT = 'house_new'
    client = MongoClient(settings.MONGO_URI)
    database = client['test']
    collection_1 = database[MONGO_COLLECTION_1]
    collection_out = database[MONGO_COLLECTION_OUTPUT]
    
    # 建立索引
    v = {
        'raw_key': {'name': 'raw_key', 'unique': True},
        'url': {'name': 'url'},
        'domain': {'name': 'domain'},
        'price': {'name':'price'},
        'size': {'name':'size'}
        }
    for key, kwargs in v.items():
        collection_out.create_index(key, background=True, **kwargs)

    # 清洗 sh.zu.fang.com
    items = []
    cur = collection_1.find().skip(st).limit(num)
    cnt = 0
    requests = []
    for item in cur:
#         print(cnt)
#         cnt += 1
#         print(item['html'])
#         print(item['raw_key'])
#         print(item['url'])
        soup = BeautifulSoup(item['html'], features="lxml")
        price_tag = soup.find(name='div', attrs={"class":"trl-item sty1"})
        if not price_tag:
            price_tag = soup.find(name='div', attrs={"class":"trl-item sty1 rel"})
        price = price_tag.i.string
        pay_way = re.search(pattern = '（.*?）', string=price_tag.text, flags=0).group().strip('（）')
        tag = [it.string for it in soup.find(name='div', attrs={'class':"bqian clearfix"}).find_all('span')] if soup.find(name='div', attrs={'class':"bqian clearfix"}) else []
        basic_info = [it.string for it in soup.find_all(name='div', attrs={'class':"tt"})]
        try:
            intro = soup.find(name='div', attrs={'class':"cont yc"}).text.strip().replace("\n\n","").replace(' ','')
        except Exception as e:
            intro = None
            
        try:
            facility = [it.string for it in soup.find(name='div', attrs={'class':"cont clearfix"}).find_all('li')]
        except Exception as e:
            facility = None
            
        try:
            community = soup.find(name='div', attrs={'class':"rcont"}).find(name='a', attrs={'id':'agantzfxq_C02_07'}).string
        except Exception as e:
            community =  soup.find(name='div', attrs={'class':"rcont"}).text
            
        address_info = [it.text.strip() for it in soup.find_all(name='div', attrs={'class':"rcont"})]
        if len(address_info) == 3:
            traffic = address_info[1]
            detail = address_info[2]
        else:
            traffic = None
            detail = address_info[1]
        try:
            pic = ['https:' + it.get('src') for it in soup.find(name='div', attrs={'class':"cont-sty1 clearfix"}).find_all(name='img', attrs={'alt':"房源图片"})]
        except Exception as e:
            pic = None
            
        # 补充address和traffic
        address = community + detail
        coordinate = get_coordinate(address, '上海')
        if not traffic or traffic.find('米')==-1:
            traffic = get_traffic(coordinate)
        
        item_out = {
            'raw_key': _hash(item['raw_key']),
            'price': price,    # 单位元每月
            'pay_way': pay_way, # 付款方式，如押一付三等
            'tag': tag,     # 房屋标签
            'rent_way': basic_info[0],  # 出租方式
            'house_type': basic_info[1], # 户型
            'size': basic_info[2],    # 面积
            'orientation': basic_info[3], # 朝向
            'floor':  basic_info[4], # 楼层
            'decorate_type': basic_info[5], # 装修类型
            'intro': intro,   # 房屋介绍
            'facility': facility, # 设施
            'traffic': traffic,
            'address': {"city": "上海", "district": item['district'], "community": community, "detail": detail, 'coordinate':coordinate},
            'pic': pic, # 房源图片
            'domain': item['domain'], #来源网站
            'url': item['raw_key'], #来源网址
        }
        requests.append(UpdateOne({'raw_key': item_out['raw_key']}, {'$set': dict(item_out)}, upsert=True))
#         for (k,v) in item_out.items():
#             print(k,':',v)
#     批处理
    collection_out.bulk_write(requests)
#     print(result.upserted_ids)
    print("[%s-%s) is ok" % (st, st+num))
    print(get_coordinate('无锡江南大学'))
    coordinate = '121.192279,31.161247'
    print(get_traffic(coordinate))


def worker_2(st, num):
    MONGO_COLLECTION_2 = 'zufang58_details_crawl'
    MONGO_COLLECTION_OUTPUT = 'house_new'
    client = MongoClient(settings.MONGO_URI)
    database = client['test']
    collection_2 = database[MONGO_COLLECTION_2]
    collection_out = database[MONGO_COLLECTION_OUTPUT]
    # 建立索引
    v = {
        'raw_key': {'name': 'raw_key', 'unique': True},
        'url': {'name': 'url'},
        'domain': {'name': 'domain'},
        'price': {'name':'price'},
        'size': {'name':'size'}
        }
    for key, kwargs in v.items():
        collection_out.create_index(key, background=True, **kwargs)
    items = []
    requests = []
    cur = collection_2.find().skip(st).limit(num)
    err_list = []
    cnt = st
    for item in cur:
#         cnt +=1
#         print(cnt)
#         print(item['raw_key'])
#         print(item['url'])
#         print(item['html'])
        soup = BeautifulSoup(item['html'], features="lxml")
        try:
            price_str = soup.find(name='b', attrs={'class':'f36 strongbox'}).string.strip()
        except Exception as e:
            err_list.append(item['url'])
            continue
        script = soup.find('head').find_all('script')[0].text  
#         try:
        price = decode(script, price_str) # 价格解密
#         except Exception as e:
#             price = price_str
#             print(price)
        pay_way = soup.find(name='span', attrs={"class":"instructions"}).text
        tag = [it.text for it in soup.find(name='ul', attrs={"class":"introduce-item"}).find_all("em")]
        basic_info = [it.text for it in soup.find(name='ul', attrs={"class":"f14"}).find_all("span")]
        house_type =  basic_info[3].strip().replace(' ','')
        house_type_list = house_type.split(b'\xc2\xa0'.decode())
                
        tmp_list = []
        tmp_list.append(decode(script, house_type_list[0][0]) + '室')
        tmp_list.append(decode(script, house_type_list[0][2]) + '厅')
        tmp_list.append(decode(script, house_type_list[0][4]) + '卫')
        size = decode(script, house_type_list[2][:-1])
        house_type = ' '.join(tmp_list)
            
        try:
            decorate_type = house_type_list[4]
        except Exception as e:
            decorate_type = None
            
        tmp_list = basic_info[5].split(b'\xc2\xa0'.decode())
        orientation = tmp_list[0]
        floor_list = []
#         print(tmp_list)
        if tmp_list[2] == '':
            floor = None
        else:
            for it in tmp_list[2].split(' / '):
                if it[0] in ['中','高','低']:
                    floor_list.append(it)
                elif it[0] == '共':
                    floor_list.append(it[0] + decode(script, it[1:-1]) + it[-1])
                else:
                    floor_list.append(decode(script, it[:-1]) + it[-1])
            floor = ' '.join(floor_list)
            
        try:
            intro = soup.find(name='ul', attrs={"class":"introduce-item"}).find_all(name='span', attrs={"class":"a2"})[1].text
        except Exception as e:
            intro = soup.find(name='ul', attrs={"class":"introduce-item"}).find_all(name='span', attrs={"class":"a2"})[0].text
            
        try:
            facility = [it.text for it in soup.find(name='ul', attrs={"class":"house-disposal"}).find_all('li')]
        except Exception as e:
            facility = None
            
        try:
            traffic = soup.find(name='em', attrs={'class':"dt c_888 f12"}).string
        except Exception as e:
            traffic = None
          
        try:
            pic = [it.get('lazy_src') for it in soup.find(name='ul', attrs={'class':"house-pic-list"}).find_all('img')]
        except Exception as e:
            pic = None
        
        detail = basic_info[11].strip()
        community = basic_info[7].strip()
        
        # 补充address和traffic
        address = community + detail
        coordinate = get_coordinate(address, '上海')
        if not traffic or traffic.find('米')==-1:
            traffic = get_traffic(coordinate)
        
        item_out = {
        'raw_key': _hash(item['raw_key']),
        'price': price,    # 单位元每月
        'pay_way': pay_way, # 付款方式，如押一付三等
        'tag': tag,     # 房屋标签
        'rent_way': basic_info[1],  # 出租方式
        'house_type': house_type, # 户型
        'size': size,    # 面积
        'orientation': orientation, # 朝向
        'floor':  floor, # 楼层
        'decorate_type': decorate_type, # 装修类型
        'intro': intro,   # 房屋介绍
        'facility': facility, # 设施
        'traffic': traffic,
        'address': {"city": "上海", "district": item['district'], "community": community, "detail": detail, 'coordinate': coordinate},
        'pic': pic, # 房源图片
        'domain': item['domain'], #来源网站
        'url': item['raw_key'], #来源网址
    }
#         for (k,v) in item_out.items():
#             print(k,':',v)
        requests.append(UpdateOne({'raw_key': item_out['raw_key']}, {'$set': dict(item_out)}, upsert=True))
    # 批处理
    collection_out.bulk_write(requests)
#     print(result.upserted_ids)
    print('len(err_list): ', len(err_list))
#     for url in err_list:
#         print(url)
    print("[%s-%s) is ok" % (st, st+num))
    print(get_coordinate('无锡江南大学'))
    coordinate = '121.192279,31.161247'
    print(get_traffic(coordinate))
        

if __name__ == '__main__':
    st = 30000
    ed = 37621
#     37621
#     worker_2(st,ed-st)
    process_num = 5
    x = math.ceil((ed-st)/process_num)
    for i in range(0, process_num):
        if(st+x*i > ed):
            break
        multiprocessing.Process(target=worker_2, args=(st+x*i, x)).start()

        
# 补充name字段
        
# import re
# import math
# import settings
# import stations_information
# import hashlib
# import logging
# import requests
# from pymongo import MongoClient, UpdateOne
# import multiprocessing
# from bs4 import BeautifulSoup

# MONGO_COLLECTION_1 = 'fang_details_crawl'
# MONGO_COLLECTION_2 = 'zufang58_details_crawl'
# MONGO_COLLECTION_OUTPUT = 'house_new'
# client = MongoClient(settings.MONGO_URI)
# database = client['test']
# collection_1 = database[MONGO_COLLECTION_1]
# collection_2 = database[MONGO_COLLECTION_2]
# collection_out = database[MONGO_COLLECTION_OUTPUT]

# st = 0
# num = 10

# cur = collection_out.find().skip(st)

# requests = []

# cnt = st

# for item in cur:
# #     print(cnt)
# #     print(item['raw_key'])
# #     print(item['url'])
# #     print(item['html'])
    
#     if item['domain'] == 'sh.zu.fang.com':
#         item_tmp = collection_1.find({"raw_key":item['url']})[0]
#         soup = BeautifulSoup(item_tmp['html'], features="lxml")
#         try:
#             name = soup.find(name='div', attrs={'class':"title"}).text.strip('\r\n ')
#         except Exception as e:
#             name = None
#     else:
#         item_tmp = collection_2.find({"raw_key":item['url']})[0]
#         soup = BeautifulSoup(item_tmp['html'], features="lxml")
#         soup = BeautifulSoup(item_tmp['html'], features="lxml")
#         # item_tmp['html']
#         name_str = soup.find(name='div', attrs={'class':"house-title"}).text.strip('\r\n ').split('\n')[0]
#         script = soup.find('head').find_all('script')[0].text
#         name = ''
#         for s in name_str:
#             name += decode(script, s)
    
#     item['name'] = name
# #     print(name)
    
#     requests.append(UpdateOne({'raw_key': item['raw_key']}, {'$set': dict(item)}, upsert=True))
#     # 批处理
#     if(len(requests)) >= 1000:
#         collection_out.bulk_write(requests)
#         requests = []
#         cnt += 1000
#         print(cnt, '...')
        
# collection_out.bulk_write(requests)
# cnt += len(requests)
# print(cnt, '...')
    
    
    
# 补充subway字段
# import re
# import math
# import settings
# import stations_information
# import hashlib
# import logging
# import requests
# from pymongo import MongoClient, UpdateOne

# MONGO_COLLECTION_OUTPUT = 'house_new'
# client = MongoClient(settings.MONGO_URI)
# database = client['test']
# collection_out = database[MONGO_COLLECTION_OUTPUT]

# st = 0
# num = 10
# cur = collection_out.find().skip(st)
# requests = []
# cnt = st

# for item in cur:
# #     print(item)
#     item['subway'] = get_traffic(item['traffic'])
#     requests.append(UpdateOne({'raw_key': item['raw_key']}, {'$set': dict(item)}, upsert=True))
#     # 批处理
# #     print(item)
#     if(len(requests)) >= 1000:
#         collection_out.bulk_write(requests)
#         requests = []
#         cnt += 1000
#         print(cnt, '...')
        
# collection_out.bulk_write(requests)
# cnt += len(requests)
# print(cnt, '...')
