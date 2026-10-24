# ROS2 CLI 工具速查

## 一、节点

```bash
# 列出所有节点
ros2 node list

# 查看某个节点的详情（发布、订阅、服务、Action）
ros2 node info /node_name

# 查看帮助
ros2 node -h
ros2 node list -h
ros2 node info -h
```

## 二、功能包

```bash
# 列出所有功能包
ros2 pkg list

# 列出某个功能包下的所有可执行程序
ros2 pkg executables <package_name>

# 创建功能包
# --build-type: ament_python 或 ament_cmake
# --dependencies: 依赖
# --node-name: 自动生成一个节点文件
ros2 pkg create <package_name> --build-type <type> --dependencies <deps> --node-name <node_name>

# 查看帮助
ros2 pkg -h
```

## 三、colcon（编译工具）

```bash
# 编译工作空间下所有包
colcon build

# 只编译指定包
colcon build --packages-select <package_name>

# 编译指定包及其依赖
colcon build --packages-up-to <package_name>

# 纯 Python 包用软链接方式安装，改代码后不用重复编译
colcon build --symlink-install --packages-select <package_name>

# 编译后刷新环境，每个新终端都要执行
source install/setup.bash

# 清理编译产物（build 和 install 目录）
rm -rf build install log
```

## 四、话题

```bash
# 列出所有话题
ros2 topic list

# 列出话题并显示类型
ros2 topic list -t

# 查看话题详情（类型、发布者数、订阅者数）
ros2 topic info /topic_name

# 查看话题 QoS 等详细信息
ros2 topic info /topic_name --verbose

# 查看话题的类型
ros2 topic type /topic_name

# 按类型查找话题
ros2 topic find <msg_type>

# 打印话题内容
ros2 topic echo /topic_name

# 只打印一条
ros2 topic echo /topic_name --once

# 手动发布消息（YAML 冒号后必须有空格）
ros2 topic pub /topic_name <msg_type> '{field: value}'

# 查看话题发布频率
ros2 topic hz /topic_name

# 查看话题带宽
ros2 topic bw /topic_name

# 查看话题延迟
ros2 topic delay /topic_name

# 查看帮助
ros2 topic -h
ros2 topic echo -h
```

## 五、服务

```bash
# 列出所有服务
ros2 service list

# 列出服务并显示类型
ros2 service list -t

# 查看服务类型
ros2 service type /service_name

# 按类型查找服务
ros2 service find <srv_type>

# 手动调用服务（YAML 冒号后必须有空格）
ros2 service call /service_name <srv_type> '{field: value}'

# 查看帮助
ros2 service -h
ros2 service call -h
```

## 六、参数

```bash
# 列出所有节点的参数
ros2 param list

# 列出指定节点的参数
ros2 param list /node_name

# 查看参数的描述、类型、约束
ros2 param describe /node_name <param_name>

# 获取参数值
ros2 param get /node_name <param_name>

# 设置参数值（临时，重启丢失）
ros2 param set /node_name <param_name> <value>

# 导出参数为 YAML（Humble 及之后需重定向保存）
ros2 param dump /node_name > <file>.yaml

# 从 YAML 加载参数（节点运行中）
ros2 param load /node_name <file>.yaml

# 查看帮助
ros2 param -h
```

## 七、动作

```bash
# 列出所有 Action
ros2 action list

# 列出 Action 并显示类型
ros2 action list -t

# 查看 Action 的客户端和服务端
ros2 action info /action_name

# 发送目标
ros2 action send_goal /action_name <action_type> '{field: value}'

# 发送目标并订阅反馈
ros2 action send_goal /action_name <action_type> '{field: value}' --feedback

# 查看帮助
ros2 action -h
```

## 八、接口

```bash
# 列出所有接口
ros2 interface list

# 查看接口定义
ros2 interface show <interface>

# 查看某个功能包里的所有接口
ros2 interface package <package_name>

# 列出所有包含接口的功能包
ros2 interface packages

# 查看帮助
ros2 interface -h
```

## 九、运行

```bash
# 运行一个功能包的可执行程序
ros2 run <package_name> <executable_name>

# 启动时设置参数
ros2 run <package_name> <executable_name> --ros-args -p <key>:=<value>

# 启动时重映射话题或节点名
ros2 run <package_name> <executable_name> --ros-args -r <from>:=<to>

# 启动时加载参数文件
ros2 run <package_name> <executable_name> --ros-args --params-file <file>.yaml

# 启动时设置日志级别
ros2 run <package_name> <executable_name> --ros-args --log-level debug

# 查看帮助
ros2 run -h
```

## 十、Launch

```bash
# 运行 launch 文件
ros2 launch <package_name> <launch_file>

# 查看 launch 文件可传的参数
ros2 launch <package_name> <launch_file> --show-args

# 启动时传参
ros2 launch <package_name> <launch_file> <arg_name>:=<value>

# 查看帮助
ros2 launch -h
```

## 十一、其他常用

```bash
# 检查 ROS 环境是否正常
ros2 doctor

# 录制话题数据
ros2 bag record /topic_name

# 查看 bag 文件信息
ros2 bag info <bag_file>

# 回放 bag 文件
ros2 bag play <bag_file>

# 查看生命周期节点状态
ros2 lifecycle list /node_name

# 查看 Domain ID
echo $ROS_DOMAIN_ID

# 忘了怎么用，加 -h
ros2 <command> -h
ros2 <command> <sub-command> -h
```

## 十二、通用规律

```bash
# list：列出某类所有东西
# info：查看某个东西的详情
# type：查看类型
# find：按类型反查
# -t：列出时带类型
# -v / --verbose：显示详细信息
# -h / --help：查看帮助
# --once：只执行一次
# --ros-args：给节点进程传 ROS2 系统参数
```
