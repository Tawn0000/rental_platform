# Create your models here.

import mongoengine

class House(mongoengine.Document):
    name = mongoengine.StringField()
    raw_key = mongoengine.StringField()
    price = mongoengine.FloatField()    # 单位元每月
    pay_way =  mongoengine.StringField() # 付款方式，如押一付三等
    tag = mongoengine.ListField()       # 房屋标签
    rent_way = mongoengine.StringField()   # 出租方式
    house_type = mongoengine.StringField()  # 户型
    size = mongoengine.FloatField()    # 面积
    orientation = mongoengine.StringField()  # 朝向
    floor =  mongoengine.StringField()  # 楼层
    decorate_type = mongoengine.StringField()  # 装修类型
    intro = mongoengine.StringField()    # 房屋介绍
    facility = mongoengine.ListField()  # 设施
    traffic = mongoengine.StringField()
    address = mongoengine.DictField()
    pic = mongoengine.ListField()   # 房源图片
    domain = mongoengine.StringField()  #来源网站
    url = mongoengine.StringField()  #来源网址

class Feedback(mongoengine.Document):
    feedback = mongoengine.StringField()
    email = mongoengine.StringField()
    created_time = mongoengine.StringField()
