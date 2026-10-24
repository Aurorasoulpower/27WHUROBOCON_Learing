---
created: 2026-10-01
type: Note
tags:
  - "#ros2"
  - "#节点通信"
---
# 节点是什么
ROS2中每一个节点也是只负责一个单独的模块化的功能
比如：
一个节点负责控制车轮转动
一个节点负责从激光雷达获取数据
一个节点负责处理激光雷达的数据
一个节点负责定位

# 节点操作
## 启动节点
ros2 run
    ↓
去ROS2环境中寻找
    ↓
某个包(package)
    ↓
里面的某个可执行程序(executable)
    ↓
启动它对应的节点(node)

命令：
```bash
ros2 run <package_name> <executable_name>
```
例如：
```bash
ros2 run turtlesim turtlesim_node
ros2 run turtlesim turtle_teleop_key
```
实际结构：
```txt
package
   |
   |-- executable
          |
          |-- node1
          |-- node2
```

## 查看节点列表
```bash
ros2 node list
```

## 查看节点详细信息

```bash
ros2 node info /节点名

#ros2 node info /turtlesim
```
输出解释：
```bash
/turtlesim
# 节点名称：/turtlesim
Subscribers:
# 作为订阅者订阅的话题（接收其他节点发送的数据）
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    # ROS2参数变化事件，系统自动生成，一般不用关注
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
    # 接收速度控制指令
    # 消息类型：Twist（线速度 + 角速度）
    # 其他节点发布这个话题，控制乌龟运动

Publishers:
# 作为发布者发布的话题（向其他节点发送数据）
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    # 发布参数变化事件
    /rosout: rcl_interfaces/msg/Log
    # 发布日志信息，用于ROS日志系统

    /turtle1/color_sensor: turtlesim/msg/Color
    # 发布乌龟脚下的颜色信息，模拟传感器数据
    /turtle1/pose: turtlesim/msg/Pose
    # 发布乌龟位姿信息
    # 包含：
    # x      位置
    # y      位置
    # theta  朝向角
    # linear_velocity 线速度
    # angular_velocity 角速度

Service Servers:
# 服务服务端
# 当前节点提供的服务接口，其他节点可以调用这些功能
    /clear: std_srvs/srv/Empty
    # 清除画布上的轨迹
    /kill: turtlesim/srv/Kill
    # 删除一只乌龟
    /reset: std_srvs/srv/Empty
    # 重置模拟环境
    /spawn: turtlesim/srv/Spawn
    # 创建新的乌龟
    /turtle1/set_pen: turtlesim/srv/SetPen
    # 设置画笔颜色、宽度等参数
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    # 直接设置乌龟位置和方向
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    # 相对当前位置移动
    
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    # 获取节点参数
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    # 修改节点参数
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    # 查看参数列表

Service Clients:
# 服务客户端
# 当前节点调用其他节点提供的服务
    None
    # /turtlesim没有调用其他Service

Action Servers:
# 动作提供端，提供长时间执行任务的接口
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
    # 控制乌龟旋转到指定角度
    # Action特点：可以持续反馈执行进度

Action Clients:
# 动作客户端，请求其他节点执行Action
	None
```


## 节点重映射（Node Remapping）

### 作用

在**不修改代码**的情况下，改变节点运行时的名称、话题名称等。
常用于：
- 同一个程序启动多个实例
- 区分不同机器人 / 传感器
- 避免节点名称冲突

---
### 命令格式
```bash
# 命令格式
ros2 run <package_name> <executable_name> \
  --ros-args --remap __node:=<new_node_name>
```

---
### 示例
```bash
# 正常启动
ros2 run turtlesim turtlesim_node

# 查看节点
ros2 node list

# 输出：
# /turtlesim


```

```bash
# 重映射节点名称启动
ros2 run turtlesim turtlesim_node \
  --ros-args --remap __node:=my_turtle

# 再次查看节点
ros2 node list

# 输出：
# /my_turtle
```
---
### 命令解析
```bash
--ros-args
```
表示：
> 后面的参数属于 ROS2 参数。
```bash
--remap
```
表示：
> 对 ROS 名称进行重新映射。
```bash
__node:=my_turtle
```
表示：
```text
原节点名称
    __node
      ↓
新节点名称
    my_turtle
```
---
### 注意：executable 和 node name 的区别

例如：
```bash
ros2 run vision vision_node
```
其中：
```text
vision
    ↓
package

vision_node
    ↓
executable（可执行程序）
```
运行后：
```bash
/vision_node
#是node name（节点名称）
```
关系：
```text
package
    ↓
executable
    ↓
node instance （节点实例）
    ↓
node name
```

---
## 启动时传入参数（Launch-time Parameters）

### 作用
在节点启动时，通过命令行给节点设置初始参数。
例如：
- 阈值
- 相机编号
- 速度限制
- 算法配置
---
### 命令格式
```bash
# 命令格式
ros2 run <package> <executable> \
  --ros-args \
  -p <parameter_name>:=<value>
```
---
### 示例
```bash
# 示例
ros2 run vision vision_node \
  --ros-args \
  -p threshold:=120 \
  -p camera_id:=1
```
---
### 命令解析
```bash
--ros-args
```
进入 ROS 参数模式。
```bash
-p threshold:=120
```
设置：
```text
threshold = 120
```
```bash
-p camera_id:=1
```
设置：
```text
camera_id = 1
```
节点启动流程：
```text
启动命令
    ↓
vision_node executable
    ↓
创建节点
/vision_node
    ↓
加载参数
threshold=120
camera_id=1
    ↓
节点运行
```

---

## 三、运行时修改参数（Runtime Parameters）

启动后，也可以动态修改参数。
### 查看参数
```bash
# 查看参数列表
ros2 param list
```

### 查看参数值
```bash
# 命令格式
ros2 param get <node_name> <parameter_name>

# 示例
ros2 param get /vision_node threshold
```

### 修改参数
```bash
# 命令格式
ros2 param set <node_name> <parameter_name> <value>

# 示例
ros2 param set /vision_node threshold 150
```

效果：

```text
threshold:
120 → 150
```

节点无需重启。

---
启动参数和运行参数区别

| 方式     | 命令               | 时间       | 作用         |
| -------- | ------------------ | ---------- | ------------ |
| 启动参数 | `-p 参数:=值`      | 节点启动时 | 设置初始配置 |
| 运行参数 | `ros2 param set`   | 节点运行中 | 动态调整配置 |

