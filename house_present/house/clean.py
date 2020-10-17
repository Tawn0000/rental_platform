import os
import sys
import pandas as pd
import numpy
import json

# 转换成数据集格式

def convert(df_input):
    # 数据集Index
    train_columns = ['size', 'traffic', 'tag_0', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5', 'tag_6', 'tag_7', 'tag_8', 'tag_9', 'tag_10', 'tag_11', 'tag_12', 'tag_13', 'tag_14', 'tag_15', 'tag_16', 'tag_17', 'tag_18', 'tag_19', 'tag_20', 'tag_21', 'tag_22', 'tag_23', 'tag_24', 'tag_25', 'tag_26', 'tag_27', 'tag_28', 'tag_29', 'tag_30', 'tag_31', 'house_type_0', 'house_type_1', 'house_type_2', 'floor_0', 'floor_1', 'floor_2', 'facility_0', 'facility_1', 'facility_2', 'facility_3', 'facility_4', 'facility_5', 'facility_6', 'facility_7', 'facility_8', 'facility_9', 'facility_10', 'facility_11', 'facility_12', 'facility_13', 'facility_14', 'facility_15', 'facility_16', 'facility_17', 'facility_18', 'facility_19', 'facility_20', 'pay_way__0', 'pay_way__1', 'pay_way__2', 'pay_way__3', 'pay_way__4', 'pay_way__5', 'pay_way__6', 'pay_way__7', 'pay_way__8', 'pay_way__9', 'pay_way__10', 'pay_way__11', 'pay_way__12', 'pay_way__13', 'rent_way_0__1', 'rent_way_0__2', 'rent_way_1__0', 'rent_way_1__1', 'rent_way_1__2', 'rent_way_1__3', 'rent_way_1__4', 'rent_way_1__6', 'rent_way_2__0', 'rent_way_2__1', 'rent_way_2__2', 'rent_way_2__3', 'orientation__0', 'orientation__1', 'orientation__2', 'orientation__3', 'orientation__4', 'orientation__5', 'orientation__6', 'orientation__7', 'orientation__8', 'orientation__9', 'orientation__10', 'decorate_type__0', 'decorate_type__1', 'decorate_type__2', 'decorate_type__3', 'decorate_type__4', 'decorate_type__5', 'address__1', 'address__2', 'address__3', 'address__4', 'address__5', 'address__6', 'address__7', 'address__8', 'address__9', 'address__10', 'address__11', 'address__12', 'address__13', 'address__14', 'address__15', 'address__16', 'address__17']

    df_res = df_input.drop(['tag', 'coordinate', 'rent_way', 'house_type', 'floor', 'facility'], axis=1)
    columns = ['tag', 'rent_way', 'house_type', 'floor', 'facility']
    print(list(df_res))
    for column in columns:
        ser = df_input[column].map(lambda x : x)
        for i in range(len(ser[0])):
            df_res[column + '_' + str(i)] = ser.map(lambda x : x[i])
    # one-hot code
    df_res = pd.get_dummies(df_res, columns=['pay_way', 'rent_way_0', 'rent_way_1', 'rent_way_2', 'orientation', 'decorate_type', 'address'], prefix=['pay_way_', 'rent_way_0_', 'rent_way_1_', 'rent_way_2_', 'orientation_', 'decorate_type_', 'address_'])
    df_res = df_res.reindex(columns=train_columns, fill_value=0)
    return df_res

# 清洗需要预测的数据

def clean(row):
    row['address'] = {
        'city': '上海',
        'district': row.get('district')[0],
        'community': row.get('community')[0],
        'details': row.get('details')[0],
    }

    res = {
            'pay_way': [get_pay_way(row.get('pay_way')[0])], # 付款方式，如押一付三等
            'tag': [get_tags(row.get('tag'))],     # 房屋标签
            'rent_way': [get_rent_way(row.get('rent_way')[0] + ' - ' + row.get('rent_loc')[0] + ' - ' + row.get('rent_gender')[0])],  # 出租方式
            'house_type': [get_house_type("%s室%s厅%s卫" % (row.get('house_type_1')[0], row.get('house_type_2')[0], row.get('house_type_3')[0]))], # 户型
            'size': [get_size(row['size'][0])],   # 面积
            'orientation': [get_orientation(row['orientation'][0])], # 朝向
            'floor': [get_floor(row.get('floor_height')[0] + ' ' + row.get('floor_num')[0])] , # 楼层
            'decorate_type': [get_decorate_type(row['decoration_type'][0])], # 装修类型
            'facility': [get_facility(row.get('facility'))],# 设施
            'traffic': [get_traffic(row.get('subway')[0])],
            'address': [get_address(row['address'])],
            'coordinate': [get_coordinate(row['address'])],
        }
    return res


def get_pay_way(pay_way):
    pay_map = {
    '': 0,
    '面议': 1,
    '押一付一': 2,
    '押一付二': 3,
    '押一付三': 4,
    '押一付半年': 5,
    '押一付一年': 6,
    '押二付一': 7,
    '押二付二': 8,
    '押二付三': 9,
    '押三付一': 10,
    '押三付三': 11,
    '半年付': 12,
    '年付': 13,
    }
    return pay_map[pay_way]


def get_tags(tags):
    tags_map = {
    '是一家人' : 0,
    '不吸烟' : 1,
    '随时看房' : 2,
    '独卫' : 3,
    '繁华地段' : 4,
    '精装修' : 5,
    '已传房本' : 6,
    '紧邻地铁' : 7,
    '家电齐全' : 8,
    '电梯房' : 9,
    '押一付一' : 10,
    '南北通透' : 11,
    '朝南' : 12,
    '不养宠物' : 13,
    '免中介费' : 14,
    '女生合租' : 15,
    '是女生': 15,
    '全装全配' : 16,
    '邻地铁' : 17,
    '公区消毒'  : 18,
    '入口检疫'  : 19,
    '租户稳定' : 20,
    '首次出租' : 21,
    '独立阳台' : 22,
    '普通装修' : 23,
    '拎包入住' : 24,
    '半年起租' : 25,
    '采光好' : 26,
    '低价出租' : 27,
    '配套齐全' : 28,
    '作息正常' : 29,
    '男生合租' : 30,
    '一年起租' : 31
    }
    res = [0 for i in range(32)]
    if not tags:
        return res
    for (k,v) in tags_map.items():
        for item in tags:
            if item.find(k) != -1:
                res[v] = 1
    return res


def get_rent_way(rent_way):
    '''
    '合租 - 主卧 - 限男生':
    '合租 - 次卧':
    '合租 - 其他':
    '合租 - 次卧 - 限女生':
    '床位(合租)':
    '合租 - 其他 - 男女不限':
    '合租 - 其他 - 限女生':
    '次卧(合租)':
    '整租':
    '隔断间(合租)':
    '合租 - 男女不限':
    '合租 - 主卧 - 限女生':
    '合租 - 主卧 - 男女不限':
    '主卧(合租)':
    '合租 - 次卧 - 限男生':
    '单间(合租)':
    '合租 - 主卧':
    '合租 - 次卧 - 男女不限':
    '''
    rent_map_list = [
                {
                    '未知': 0,
                    '合租': 1,
                    '整租':2,
                },
                {
                    '未知': 0,
                    '其他': 0,
                    '主卧': 1,
                    '次卧': 2,
                    '隔断间': 3,
                    '床位': 4,
                    '单间': 6,
                },
                {
                    '未知': 0,
                    '男': 1,
                    '女': 2,
                    '不限': 3,
                }
              ]
    res = [0 for i in range(3)]
    for (i,rent_map) in enumerate(rent_map_list):
        for (k,v) in rent_map.items():
            if rent_way.find(k) != -1:
                res[i] = v
    return res


def get_house_type(house_type):
    house_type = house_type.replace(' ','')
    res = [-1 for i in range(3)]
    tmp = house_type.split('室')
    if len(tmp) == 2:
        res[0] = int(tmp[0])
        tmp = tmp[1].split('厅')
        res[1] = int(tmp[0])
        tmp = tmp[1].split('卫')
        res[2] = int(tmp[0])
    return res


def get_size(size):
    size = float(size.replace('平米',''))
    return size


def get_orientation(orientation):
    orientation_map = {
        '东' : 1,
        '南' : 2,
        '西' : 3,
        '北' : 4,
        '东南' : 5,
        '东北' : 6,
        '西南' : 7,
        '西北' : 8,
        '东西' : 9,
        '南北' : 10,
        '暂无信息' : 0,
        '暂无' : 0,
        '不限' : 0
    }
    return orientation_map[orientation]

def get_floor(floor):
#     floor = '共2层'
    floor_map = {
        '高层': 1,
        '中层': 2,
        '低层': 3,
        '地下': 4
    }
    res = [0, 0, 0]
    if not floor:
        return res
    elif floor[0] == '共':
        res[0] = (int)(floor.strip('共层'))
    else:
        res[0] = 1
        tmp = floor.split(' ')
        if len(tmp) >= 1:
            res[1] = floor_map[tmp[0]]
        if len(tmp) >= 2:
            res[2] = (int)(tmp[1].replace('层', ''))
    return res


def get_decorate_type(decorate_type):
    res = 0
    decorate_type_map = {
    '未知': 0,
    '毛坯': 1,
    '简单装修': 2,
    '中等装修': 3,
    '精装修': 4,
    '豪华装修': 5,
    '中装修': 3,
    '暂无资料': 0,
    '不限':0,
    '简装修':2,
     None: 0
    }
    return decorate_type_map[decorate_type]

def get_facility(facility):
    facility_map = {
    '卫生间' : 0,
    '独立卫生间' : 1,
    '冰箱' : 2,
    '宽带' : 3,
    '可做饭' : 4,
    '衣柜' : 5,
    '露台' : 6,
    '阁楼' : 7,
    '暖气' : 8,
    '洗衣机' : 9,
    '游泳池' : 10,
    '车位' : 11,
    '微波炉' : 12,
    '沙发' : 13,
    '床' : 14,
    '阳光房' : 15,
    '空调' : 16,
    '热水器' : 17,
    '电视' : 18,
    '阳台' : 19,
    '电梯' : 20
    }
#     facility = ['独立卫生间', '冰箱', '宽带', '可做饭', '衣柜', '露台', '阁楼', '暖气', '洗衣机', '游泳池', '车位', '微波炉', '卫生间', '沙发', '床', '阳光房', '空调', '热水器', '电视', '阳台', '电梯']

    res = [0 for i in range(21)]
    if not facility:
        return res
    for (k,v) in facility_map.items():
        if k in facility:
            res[v] = 1
    return res


def get_traffic(traffic):
#     traffic = '距离地铁5号线南延伸段金海湖站站880米'
#     无邻近地铁则设置为3000米，因为大于2000米非地铁房
    if not traffic:
        return 3000
    traffic = traffic.strip('米')
    res = ''
    for c in traffic[::-1]:
        if c >= '0' and c <= '9':
            res += c
        else:
            break
    if res == '':
        res = 3000
    else:
        res = int(res[::-1])
    return res

def get_address(address):
    district = address['district']
    address_map = {
        '黄浦':1,
        '嘉定':2,
        '普陀':3,
        '上海周边':4,
        '浦东':5,
        '徐汇':6,
        '静安':7,
        '松江':8,
        '青浦':9,
        '杨浦':10,
        '虹口':11,
        '崇明':12,
        '奉贤':13,
        '长宁':14,
        '金山':15,
        '宝山':16,
        '闵行':17
    }
    res = address_map[district]
    return res
def get_coordinate(address):
    if address.get('coordinate'):
        res = [float(item) for item in address['coordinate'].split(',')]
    else:
        res = None
    return res
