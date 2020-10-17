# 版本信息
# Hadoop：3.2.1_1
# Spark：2.4.5
# Scala：2.11.12
# Java：1.8.0_241
# Mongo：4.2.3
# mongo-java-driver-3.12.2.jar
# mongo-spark-connector_2.11-2.4.1.jar

import settings
import datetime

MONGO_URI = settings.MONGO_URI + '/test.house' # 数据库表名

now_time=datetime.datetime.now()
pre_time=(now_time + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S") #获取前一天,为之后的增量提供时间点

# 从mongo数据库load数据
df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",MONGO_URI).load()

# 将房源数据分区存储入hdfs
df.repartition(40).write.parquet("shanghai.house.parquet")