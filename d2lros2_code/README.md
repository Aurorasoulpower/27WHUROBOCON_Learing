# ROS2 学习记录

## 📁 目录说明

- **chapt2/**：第2章 ROS2第一个节点相关代码
- **chapt3/**：第3章 节点通信（话题与服务）相关代码
  - **chapt3_ws/src/example_ros2_interfaces/**：自定义接口包（msg/srv）
  - **chapt3_ws/src/example_interfaces_rclpy/**：Python自定义接口实战（机器人节点+控制节点）
- **chapt4/**：第4章 参数、动作与生命周期相关代码
  - **chapt4_ws/src/example_param_rclpy/**：参数节点实操（含参数回调版）
  - **chapt4_ws/src/robot_control_interfaces/**：Action 接口包（MoveRobot.action）
  - **chapt4_ws/src/example_action_rclpy/**：Action 实战（服务端+客户端，含取消功能）
- **doc/**：学习笔记及日志记录存放处
  - **doc/学习日志记录.md** 日志
  - **其他ros2开头的** 笔记
  - **日期开头的** 实操记录

## 📝 进度记录

- [X] 第2章 第一个节点
- [X] 第3章 话题与服务基础
- [X] 第3章 自定义接口与Python实战
- [X] 第3章 QoS 配置与不兼容排查
- [X] 第3章 通信底层与 DDS 认知
- [X] 第4章 参数通信（CLI、声明、读取、设置）
- [X] 第4章 参数回调（替代轮询）
- [X] 第4章 Action 通信（接口定义、服务端、客户端、取消）
- [X] 第4章 生命周期节点（概念）
- [X] 第5章 常用工具（launch，CLI ， RViz ， RQT，Rosbag ，Gazebo简单认识)

## 💻 环境

- Ubuntu 20.04
- ROS 2  Humble
- Python 3.8+

## 📌 备忘

- 编译：`colcon build`
- 只编译单个包：`colcon build --packages-select <包名>`
- 编译到某个包及其依赖：`colcon build --packages-up-to <包名>`
- 刷新环境：`source install/setup.bash`（每个新终端都要执行）
- 接口包改动后必须重新编译，不能用 `--symlink-install` 跳过
- 纯 Python 逻辑改动可以加 `--symlink-install`，避免反复编译

## 🔍 常用排查命令

- 查看节点：`ros2 node list`
- 查看话题：`ros2 topic list`
- 查看话题 QoS：`ros2 topic info <话题> --verbose`
- 查看服务：`ros2 service list`
- 查看参数：`ros2 param list`
- 查看 Action：`ros2 action list -t`
- 查看接口：`ros2 interface show <接口>`
- 查看 Domain ID：`echo $ROS_DOMAIN_ID`
- 系统诊断：`ros2 doctor`
