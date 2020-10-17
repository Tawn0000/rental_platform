#！ /bin/bash

# dirname $0，取得当前执行的脚本文件的父目录
basepath=$(cd `dirname $0`; pwd)

# 进入到SPARK所在的目录
cd ${SPARK_HOME}

# 打印当前路径
currentPath=$(pwd)
echo "当前文件夹路径: $currentPath"

# 启动spark
sbin/start-all.sh

# 进入Hadoop所在的目录
cd "/usr/local/Cellar/hadoop/3.2.1_1/"

# 打印当前路径
currentPath=$(pwd)
echo "当前文件夹路径: $currentPath"

# 启动Hadoop
sbin/start-all.sh

# 查看jps
jps
