1. 目录结构
.
├── Readme.md
├── clean_item.ipynb 从Mongo中提取爬取回来的数据，提取房源信息，再存入MongoDB：house, 注意：不同来源的房源数据处理过程不一样，最终的字段结构统一
├── clean_item.py
├── get_dataset.ipynb  制作数据集                需要启动Spark，使用pyspark+Ipython运行  
├── get_statics.ipynb  统计房源数据信息           需要启动Spark，使用pyspark+Ipython运行  
├── get_traffic.ipynb  高得API脚本
├── mongodb2hdfs.ipynb 将MongoDB的数据转存入HDFS，需要启动Spark，使用pyspark+Ipython运行  
├── mongodb2hdfs.py
├── settings.py        配置文件
├── shanghai.house.csv Spark清洗完的数据集
│   ├── _SUCCESS
│   └── part-00000-e9642b57-ab0f-47d8-ab90-e1eccc8b6560-c000.csv
├── start.sh   hadoop 和 spark 启动脚本
└── stations_information.py   地铁站点数据

2. 运行顺序：
clean_item -> mongodb2hdfs -> get_dataset(get_statics)

注：[Spark的安装和配置](https://tawn0000.github.io/2020/03/26/installation-and-configuration-of-spark/)
