---
created: 2026-09-30
tags:
  - "#linux"
  - "#ros2"
type: Note
---


**文件/目录**

```bash
pwd        # 当前目录
ls         # 查看文件
cd         # 切换目录
find       # 查找文件/目录
grep       # 筛选文本
```

**C++ 编译**

```bash
g++ xxx.cpp             # 编译
-I/path                 # 头文件搜索路径
-L/path                 # 库搜索路径
-lxxx                   # 链接 libxxx
-o name                 # 指定输出文件名
./a.out                 # 运行程序
```

**Shell**

```bash
\          # 换行继续输入
$(...)     # 执行命令并把结果嵌入当前命令
```

**ROS2**

```bash
source /opt/ros/humble/setup.bash   # 加载 ROS2 环境
ros2 node list                      # 查看节点
ros2 node info /xxx                 # 查看节点详情
```

**最核心：**

```text
-I → 找头文件
-L → 找库
-l → 用哪个库
```


示例：
```bash
$ pwd
/home/aurora/d2lros2/chapt2/basic

$ ls
first_ros2_node.cpp

$ find /opt/ros/humble/include -name rclcpp.hpp
/opt/ros/humble/include/rclcpp/rclcpp/rclcpp.hpp

$ grep rclcpp first_ros2_node.cpp
#include "rclcpp/rclcpp.hpp"

$ g++ first_ros2_node.cpp \
  -I/opt/ros/humble/include/rclcpp/ \
  -L/opt/ros/humble/lib/ \
  -lrclcpp \
  -lrcutils \
  -o first_node

$ ls
first_node  first_ros2_node.cpp

$ ./first_node
# 没有输出，程序持续运行

```

  ```bash
# 新开终端
$ source /opt/ros/humble/setup.bash

$ ros2 node list
/first_node

$ ros2 node info /first_node
/first_node
  Subscribers:
  Publishers:
  Service Servers:
  ```
