---
type: Note
created: 2026-09-29
tags:
  - "#ros2"
---

# 系统架构
![[系统架构.png]]
对于开发者而言，关注应用层和客户端层
## 操作系统
ROS2本身就是基于Linux、Windows或者macOS系统建立的，驱动计算机硬件、底层网络通信等实现都是交由操作系统来实现的。

## DDS实现
Data Distribution Service (数据分发服务)
其实就是对不同常见的DDS接口进行再次的封装，让其保持统一性，为DDS抽象层提供统一的API。这使得 ROS 2 能够提供各种优质的Qos服务策略，从而改善不同网络的通信。

## DDS接口（抽象）RMW
这一层将DDS实现层进一步的封装，使得DDS更容易使用。原因在于DDS需要大量的设置和配置（分区，主题名称，发现模式，消息创建,...），这些设置都是在ROS2的抽象层中完成的。

## ROS2客户端库RCL
RCL（ROS Client Library）ROS客户端库，其实就是ROS的一种API，提供了对ROS话题、服务、参数、Action等接口。

> 多语言Ros库

|语言|地址|
|---|---|
|python-rclpython|	https://github.com/ros2/rclpy|
|c++ - rclcpp	|https://github.com/ros2/rclcpp|
|java-rcljava	|https://github.com/esteve/ros2_java|
|rust-rclrust	|https://github.com/ros2-rust/ros2_rust|
|node.js-rclnodejs	|https://github.com/RobotWebTools/rclnodejs|
|go-rclgo	|https://github.com/juaruipav/rclgo|
|lua-rcllua	|https://github.com/jbbjarnason/rcllua|
|kotlin-rclkin	|https://github.com/ros2java-alfred/ros2_kotlin|
|swift-rclswift	|https://github.com/atyshka/ros2_swift|
|c#-rclcs	|https://github.com/RobotecAI/ros2cs|

# ROS2 的核心是通信，优势是完整生态
## 话题TOPIC

基于发布-订阅式的通信方式，允许节点之间异步交换数据
## 服务
同步通信方式，客户端发送请求，服务端处理并返回结果
## 参数
用于机器人参数的设置和读取

## 动作
支持复杂行为的通信方式，服务端可以反馈处理进度，客户端可以取消请求

# ROS2的局限性

- 机器人操作系统并不是真的操作系统，受操作系统限制！系统BUG也是你的BUG
	- 本身做不到实时性!硬实时还需依赖操作系统
- 通信速度受内存速度、网速等物理层限制
- 大而全，注定和小而美此生无缘


