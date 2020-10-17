from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
# Create your views here.
# .表示当前包下的models
from .models import House, Feedback
from .predict import predict
from django.views.generic import View
import random
import json
import re
import math
import datetime

class House_view(View):
    def index(request):
        return render(request, 'index.html', context={'title':"主页", 'empty':range(50)})

    def rent(request):
        print(request.GET)

        # 标签和设施前缀设置
        path_prefix_list = []
        for (k, v) in request.GET.items():
            if k not in ['tag','facility']:
                path_prefix_list.append(k + '=' + v)

        tags = request.GET.getlist('tag')
        facilities = request.GET.getlist('facility')

        path_prefix = '&'.join(path_prefix_list)

        if tags:
            if path_prefix:
                path_prefix += '&'
            path_prefix += '&'.join(['tag='+tag for tag in tags])

        if facilities:
            if path_prefix:
                path_prefix += '&'
            path_prefix += '&'.join(['facility='+facility for facility in facilities])

        if path_prefix:
            path_prefix += '&'
        # print("******")
        # print(facilities)
        # print(path_prefix)

        path_prefix_map = {
            'district': '&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'district']),
            'price': '&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'price']),
            'subway':'&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'subway']),
            'house_type':'&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'house_type']),
            'rent_way':'&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'rent_way']),
            'orientation':'&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'orientation']),
            'origin':'&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'origin']),
            'page': '&'.join([k + '=' + v for (k, v) in request.GET.items() if k != 'page']),
        }

        for k in path_prefix_map.keys():
            if path_prefix_map[k]:
                 path_prefix_map[k] =  path_prefix_map[k] + '&'

        path_prefix_f = '/rent?'
        path_prefix_b = ''

        district_map = {
            '浦东':5,
            '嘉定':2,
            '宝山':16,
            '闵行':17,
            '松江':8,
            '普陀':3,
            '静安':7,
            '黄浦':1,
            '虹口':11,
            '青浦':9,
            '奉贤':13,
            '金山':15,
            '杨浦':10,
            '徐汇':6,
            '长宁':14,
            '崇明':12,
            '上海周边':4
        }
        price_map = {
            '0-1000': '1000以下',
            '1000-1500': '1000-1500元',
            '1500-2000': '1500-2000元',
            '2000-3000': '2000-3000元',
            '3000-5000': '3000-5000元',
            '5000-8000': '5000-8000元',
            '8000-10000000': '8000元以上'
        }

        subway_map = {
            '0-100': '100米以内',
            '0-300': '300米以内',
            '0-500': '500米以内',
            '0-1000': '1000米以内',
            '0-2000': '2000米以内'
        }

        house_type_map = {
            '1室': '一居',
            '2室': '二居',
            '3室': '三居',
            '4室': '四居',
            '5室': '五居',
        }

        rent_way_map = {
            '整租': '整租',
            '合租': '合租'
        }
        orientation_map = {
            '东' : '东',
            '南' : '南',
            '西' : '西',
            '北' : '北',
            '东南' : '东南',
            '东北' : '东北',
            '西南' : '西南',
            '西北' : '西北',
            '东西' : '东西',
            '南北' : '南北',
        }

        origin_map = {
            'sh.zu.fang.com': '房天下',
            'sh.58.com': '58同城',
        }

        query_dict = {}
        if request.GET.get("district"):
            query_dict["address.district"] = request.GET.get("district")

        where_list = []

        if request.GET.get("price"):
            price_list = [p for p in request.GET.get("price").split('-')]
            where_list.append("this.price >= %s && this.price <= %s" % (price_list[0], price_list[1]))

        if request.GET.get("subway"):
            subway_list = [s for s in request.GET.get("subway").split('-')]
            where_list.append("this.subway >= %s && this.subway <= %s" % (subway_list[0], subway_list[1]))

        if where_list:
            query_dict["$where"] = '&&'.join(where_list)

        # {$where:function(){return this.age>3}}

        if request.GET.get("house_type"):
            house_type = request.GET.get("house_type")
            query_dict["house_type"] = {
            '$regex': house_type
            }

        if request.GET.get("rent_way"):
            rent_way = request.GET.get("rent_way")
            query_dict["rent_way"] = {
            '$regex': rent_way
            }

        if request.GET.get("orientation"):
            query_dict["orientation"] = request.GET.get("orientation")

        if request.GET.get("origin"):
            query_dict["domain"] = request.GET.get("origin")

        if tags:
            query_dict["tag"] = {
            '$all': tags
            }

        if facilities:
            query_dict["facility"] = {
            '$all': facilities
            }

        facility1 = ['独立卫生间', '冰箱', '宽带', '可做饭', '衣柜', '露台', '阁楼', '暖气', '洗衣机', '游泳池']
        facility2 = ['车位', '微波炉', '卫生间', '沙发', '床', '阳光房', '空调', '热水器', '电视', '阳台', '电梯']

        tags1 = ['是一家人', '不吸烟', '随时看房', '独卫', '繁华地段', '精装修', '已传房本', '紧邻地铁', '家电齐全', '电梯房', '押一付一']
        tags2 = ['南北通透', '朝南', '不养宠物', '免中介费', '女生合租', '是女生', '全装全配', '邻地铁', '公区消毒', '入口检疫', '租户稳定']
        tags3 = ['首次出租', '独立阳台', '普通装修', '拎包入住', '半年起租', '采光好', '低价出租', '配套齐全', '作息正常', '男生合租', '一年起租']

        page_now = request.GET.get('page')
        if page_now:
            page_now = int(page_now)
        else:
            page_now = 1

        print(query_dict)
        house_num = House.objects(__raw__=query_dict).count()
        result = House.objects(__raw__=query_dict).skip((page_now-1)*10).limit(10)
        # print(house_num)
        houses = json.loads(result.to_json())

        context = {
            'title': "我要租房",
            'path_prefix': path_prefix,
            'path_prefix_f': path_prefix_f,
            'path_prefix_b': path_prefix_b,
            'path_prefix_map': path_prefix_map,
            'district_map': district_map,
            'price_map': price_map,
            'subway_map': subway_map,
            'house_type_map': house_type_map,
            'rent_way_map': rent_way_map,
            'orientation_map': orientation_map,
            'origin_map': origin_map,
            'facilities': facilities,
            'facility1': facility1,
            'facility2': facility2,
            'tags': tags,
            'tags1': tags1,
            'tags2': tags2,
            'tags3': tags3,
            'page_num': math.ceil(house_num/10),
            'page_now': page_now,
            'page_next': page_now+1,
            'page_end': math.ceil(house_num/10),
            'page_list': range(int((page_now-1)/5)*5+1, int((page_now-1)/5)*5+1+5),
            # 'more':
            'request_get': dict((k,v) for (k, v) in request.GET.items()),
            'houses': houses,
        }
        return render(request, 'rent.html', context=context)


    def predict(request):
        context = {
            'request_method': request.method,
            'request_post': json.dumps(dict(request.POST)),
            'title': "房价预测",
            'district_list': ['浦东', '嘉定', '宝山', '闵行', '松江', '普陀', '静安', '黄浦', '虹口', '青浦', '奉贤', '金山', '杨浦', '徐汇', '长宁', '崇明', '上海周边'],
            'rent_way_list': ['合租', '整租'],
            'rent_loc': ['主卧', '次卧', '隔断间', '床位', '单间'],
            'rent_gender': ['不限', '限男生','限女生'],
            'orientation_list': ['东', '南', '西', '北', '东南', '东北', '西南', '西北', '东西', '南北'],
            'floor_height': ['高层','中层','低层', '地下'],
            'decoration_type_list':['精装修', '毛坯', '简单装修', '中等装修', '豪华装修', '中装修', '简装修'],
            'facility1': ['独立卫生间', '冰箱', '宽带', '可做饭', '衣柜', '露台', '阁楼', '暖气', '洗衣机', '游泳池'],
            'facility2': ['车位', '微波炉', '卫生间', '沙发', '床', '阳光房', '空调', '热水器', '电视', '阳台', '电梯'],
            'tags1': ['是一家人', '不吸烟', '随时看房', '独卫', '繁华地段', '精装修', '已传房本', '紧邻地铁','家电齐全'],
            'tags2': ['电梯房', '押一付一', '南北通透', '朝南', '不养宠物', '免中介费', '女生合租', '是女生'],
            'tags3': ['全装全配', '邻地铁', '公区消毒', '入口检疫', '租户稳定', '首次出租', '独立阳台', '普通装修'],
            'tags4': ['拎包入住', '半年起租', '采光好', '低价出租', '配套齐全', '作息正常', '男生合租', '一年起租'],
            'pay_way_list': ['面议', '押一付一', '押一付二', '押一付三', '押一付半年', '押一付一年', '押二付一', '押二付二', '押二付三', '押三付一', '押三付三', '半年付', '年付'],
        }
        print(dict(request.POST))
        if request.method == 'POST':
            context['predict_price'] = predict(dict(request.POST))
        return render(request, 'predict.html', context=context)

    def feedback(request):
        if request.method == 'POST':
            Feedback.objects.create(feedback=request.POST.get("feedback"), email=request.POST.get('email'), created_time=str(datetime.datetime.now()))
        #     return JsonResponse(data=request.POST)
        return render(request, 'feedback.html', context={'title':"反馈建议"})

# def hello(request):
#     response = HttpResponse("<div><center><h1>hello</h1></center></div>")
#     response.write("哈哈哈")
#     response.flush()
#     url = reverse("index")
#     if random.randrange(1,10) > 5:
#         return redirect(url)
#     return response

#
# def test(request):
#     return render(request, 'test.html')
#
# def temp(request):
#     return render(request, 'temp.html', context={'title':'temp'})
#
# def post_test(request):
#     return render(request, 'post_test.html', context={'title':'上传测试'})
#

#
# def get_first(request):
#     result = House.objects(__raw__={"address.district":'静安'}).first()
#     data = json.loads(result.to_json())
#     return JsonResponse(data=data)
