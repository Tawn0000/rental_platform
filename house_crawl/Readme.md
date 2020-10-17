1. 目录结构
.
├── Readme.md
├── house_crawl
│   ├── __init__.py
│   ├── deltafetch.py        # 爬虫deltafetch中间件，利于增量爬取
│   ├── ip_proxy             # 添加IP代理的一些脚本
│   │   ├── dailiyun.py
│   │   ├── ip_proxies.ipynb
│   │   ├── ip_proxy.ipynb
│   │   ├── ip_proxy.py
│   │   ├── ip_proxy_validate.ipynb
│   │   └── test_ip.py
│   ├── items.py             # 字段
│   ├── middlewares.py       # 中间件
│   ├── pipelines.py         # 管道
│   ├── settings.py          # scrapy框架配置
│   └── spiders              # 爬虫
│       ├── __init__.py
│       ├── fang_details.py     # 房天下详情页
│       ├── fang_list.py        # 房天下列表页
│       ├── zufang58_details.py # 58租房详情页
│       └── zufang58_list.py    # 58租房列表页
└── scrapy.cfg

2. 采用MongoDB存储

3. 可增量爬取

4. 不足：由于缺乏资源，没有使用IP代理，所以需要手动填验证码进行增量