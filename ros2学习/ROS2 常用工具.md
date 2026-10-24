---
created: 2026-10-06
type: Note
tags:
  - "#ros2"
  - 仿真
---
# ROS2 常用工具笔记

## 一、RVIZ2

### 1.1 定位

数据可视化工具。把已经在话题上流动的数据，用图形界面的方式显示出来。

**核心特征**：不生产数据，只显示数据。

### 1.2 和 Gazebo 的区别

| 工具 | 做什么 | 数据从哪来 |
|------|--------|------------|
| RVIZ2 | 把已有数据显示出来 | 话题上已有数据 |
| Gazebo | 模拟环境，产生数据 | 仿真器计算生成 |

一句话：RVIZ2 是搬运工，Gazebo 是生产者。

### 1.3 全局配置

**Fixed Frame**

最重要的配置。告诉 RVIZ2 所有坐标相对于哪个坐标系显示。

常见值：

- `map`：地图坐标系，导航场景用
- `odom`：里程计坐标系
- `base_link`：机器人基座
- 相机相关 frame：显示相机数据时用

**设置错了会怎样**：所有依赖 TF 的显示都出不来，左侧 `Global Status` 报 `No tf data`。

**Frame Rate**

3D 视图刷新频率上限。默认 30，够用。

### 1.4 常用显示类型

| 显示类型 | 显示什么 | 需要的话题类型 |
|----------|----------|----------------|
| Grid | 参考网格 | 无，本地生成 |
| RobotModel | 机器人模型 | `robot_description` |
| TF | 坐标系树 | `/tf`、`/tf_static` |
| LaserScan | 激光雷达数据 | `sensor_msgs/LaserScan` |
| PointCloud2 | 点云 | `sensor_msgs/PointCloud2` |
| Image | 图像 | `sensor_msgs/Image` |
| Map | 栅格地图 | `nav_msgs/OccupancyGrid` |
| Path | 路径 | `nav_msgs/Path` |
| Marker / MarkerArray | 自定义标记 | `visualization_msgs/Marker` |
| Pose / Odometry | 位姿、里程计 | `geometry_msgs/PoseStamped`、`nav_msgs/Odometry` |

### 1.5 添加显示的步骤

1. 左下角点 `Add`
2. 弹出窗口里选类型，双击
3. 左侧出现该显示项，展开
4. 找到 `Topic` 那一行，点右侧空白，下拉选话题
5. 必要时改 QoS（见下）

### 1.6 QoS 不兼容问题

RVIZ2 的订阅默认 QoS 是 `Reliable`。而 Gazebo 相机、激光雷达等传感器发布的数据，默认是 `Best effort`。

两者不兼容时，RVIZ2 收不到数据，显示 `No Image` 或空白。

**解决**：在显示项里找 `Topic` → `Reliability Policy`，改成 `Best Effort`。

### 1.7 配置的保存和加载

菜单 `File` → `Save Config As`，保存成 `.rviz` 文件。

`File` → `Open Config` 加载。

工程中把 `.rviz` 文件放功能包里，用 launch 启动时自动加载。

### 1.8 显示不出来的排查顺序

1. Fixed Frame 是否设置正确
2. 数据的话题是否存在：`ros2 topic list`
3. 话题类型是否和显示类型匹配：`ros2 topic info /xxx -t`
4. QoS 是否兼容：`ros2 topic info /xxx --verbose`
5. TF 链路是否完整：`ros2 topic echo /tf_static --once`
6. Topic 那一行是否选了话题

### 1.9 常见易错点

| 现象 | 原因 | 解决 |
|------|------|------|
| 显示 `No Image` | Topic 没选或 QoS 不兼容 | 选话题，改 Best Effort |
| 左上角报 `No tf data` | Fixed Frame 不存在 | 改成存在的 frame |
| 模型显示不出来 | `robot_description` 没发布 | 启动 `robot_state_publisher` |
| 传感器数据不显示 | QoS 不兼容 | 显示项里改 Best Effort |

## 二、RQT

### 2.1 定位

图形化调试工具集。通过插件的方式提供各种界面工具。

**核心特征**：本身只是个框架，具体功能由插件实现。像一个插座，插件像电器。

### 2.2 启动

```bash
rqt
```

打开后界面是空的。要加插件，从菜单 `Plugins` 里选。

### 2.3 常用插件

| 菜单路径 | 插件 | 作用 |
|----------|------|------|
| Introspection / Node Graph | 节点关系图 | 查看节点和话题的连接 |
| Introspection / Process Monitor | 进程监控 | 查看 ROS 相关进程 CPU/内存 |
| Topics / Message Publisher | 图形化发话题 | 替代 `ros2 topic pub` |
| Topics / Topic Monitor | 话题监控 | 查看多个话题的发布频率 |
| Services / Service Caller | 图形化调服务 | 替代 `ros2 service call` |
| Visualization / Plot | 曲线绘制 | 看数值随时间变化，调 PID 用 |
| Visualization / Image View | 图像显示 | 看图像话题 |
| Visualization / TF Tree | 坐标系树 | 看 TF 结构 |
| Configuration / Dynamic Reconfigure | 参数修改 | 替代 `ros2 param set` |
| Logging / Console | 日志查看 | 过滤日志 |

### 2.4 Node Graph 详解

最常用的插件。

显示内容：

- 圆形/矩形：节点
- 方框：话题
- 连线：发布/订阅关系

用途：

- 一眼看清谁在发布、谁在订阅
- 排查“某个话题为什么没人收”
- 系统大了以后理清连接关系

这个插件在 ROS1 里叫 `rqt_graph`，ROS2 里正式名字是 `Node Graph`。

### 2.5 Plot 详解

调 PID 的神器。

操作：

1. 点 `+` 添加曲线
2. 选话题，比如 `/turtle1/pose`
3. 选字段，比如 `x`
4. 再添加一条，选 `y`

用途：

- 调 PID：把目标值和实际值都画出来，看超调、振荡、收敛速度
- 看传感器数值波动
- 排查某变量是否正常变化

### 2.6 Dynamic Reconfigure 详解

图形化改参数。

操作：

1. 左侧列出所有节点，选一个
2. 右侧显示该节点的所有参数
3. 修改参数值

用途：

- 改参数后立即看效果，不用敲命令行
- 参数多的节点，图形化更方便

**前提**：参数必须声明为可动态修改。只读参数无法通过它改。

### 2.7 和命令行的分工

| 场景 | 用谁 |
|------|------|
| 快速查看、脚本自动化 | 命令行 |
| 可视化交互、调曲线 | RQT |
| 看节点连接关系 | RQT 的 Node Graph |
| 调 PID 看曲线 | RQT 的 Plot |
| 改参数看效果 | RQT 的 Dynamic Reconfigure |

### 2.8 插件安装

常用插件包含在 `ros-humble-rqt-common-plugins` 里，一般随 ROS2 一起装。

额外插件：

```bash
sudo apt install ros-humble-rqt-top \
                 ros-humble-rqt-tf-tree \
                 ros-humble-rqt-robot-monitor \
                 ros-humble-rqt-runtime-monitor
```

### 2.9 常见易错点

| 现象 | 原因 | 解决 |
|------|------|------|
| 某个插件找不到 | 没装对应包 | 查包名，`apt install` |
| 插件不显示新安装的 | rqt 界面缓存 | `rm -rf ~/.config/ros.org/rqt_gui.ini`，重启 |
| 命令 `rqt_image_view` 找不到 | 不是 shell 命令，是 ROS 包 | 用 `ros2 run rqt_image_view rqt_image_view` 或从 rqt 菜单进 |

## 三、Gazebo

### 3.1 定位

物理仿真工具。根据机器人模型和传感器配置，创造一个虚拟环境，模拟物理规律，产生仿真数据。

**核心特征**：不搬运数据，只生产数据。

### 3.2 和 ROS2 的关系

Gazebo 是**独立软件**，可以脱离 ROS 使用。ROS2 和 Gazebo 之间的桥接靠一组包：`gazebo_ros_pkgs`。

数据流：

```
Gazebo 仿真世界
      ↕
gazebo_ros_pkgs（翻译层）
      ↕
ROS2 话题/服务/Action
      ↕
你的 ROS2 节点
```

### 3.3 gazebo_ros_pkgs 包含的包

| 包名 | 作用 |
|------|------|
| `gazebo_dev` | 开发 Gazebo 插件的 API |
| `gazebo_msgs` | ROS2 和 Gazebo 之间的接口定义 |
| `gazebo_ros` | C++ 类和函数，供插件使用 |
| `gazebo_plugins` | 一系列现成插件 |

常用插件：

- `gazebo_ros_camera`：发布图像话题
- `gazebo_ros_diff_drive`：两轮差速驱动
- `gazebo_ros_ray_sensor`：激光雷达

### 3.4 安装

```bash
# 装 Gazebo 本体
sudo apt install gazebo

# 装 ROS2 桥接包和插件
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-plugins
```

**包名注意**：是 `ros-humble-`，不是 `ros-bumble-`。

### 3.5 启动 Gazebo

```bash
# 新终端，先 source
source /opt/ros/humble/setup.bash

# 启动一个 world
gazebo /opt/ros/humble/share/gazebo_plugins/worlds/gazebo_ros_camera_demo.world
```

**source 是必须的**。不 source 的话，Gazebo 找不到 ROS2 插件，话题不会出来。

### 3.6 自带的 world 文件

```bash
ls /opt/ros/humble/share/gazebo_plugins/worlds/
```

常见的：

| world | 内容 |
|-------|------|
| `gazebo_ros_camera_demo.world` | 带相机 |
| `gazebo_ros_diff_drive_demo.world` | 两轮差速小车 |
| `gazebo_ros_ray_sensor_demo.world` | 带激光雷达 |
| `gazebo_ros_imu_sensor_demo.world` | 带 IMU |

### 3.7 验证 Gazebo 是否正常工作

```bash
ros2 topic list -t
```

正常情况下应该能看到：

```
/clock [rosgraph_msgs/msg/Clock]
/demo/cmd_demo [geometry_msgs/msg/Twist]
/demo/odom_demo [nav_msgs/msg/Odometry]
/tf [tf2_msgs/msg/TFMessage]
/camera/image_raw [sensor_msgs/msg/Image]       # 如果 world 有相机
...
```

**只有 `/parameter_events` 和 `/rosout`**：说明 Gazebo 和 ROS2 没连上，插件没加载。检查是否 source 了，`gazebo-plugins` 是否装了。

### 3.8 控制小车动起来

```bash
ros2 topic pub /demo/cmd_demo geometry_msgs/msg/Twist \
  "{linear: {x: 0.2, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}"
```

- `linear.x`：前进速度
- `angular.z`：转向角速度

Ctrl+C 停止发布，小车慢慢停下。

### 3.9 查看里程计

```bash
ros2 topic echo /demo/odom_demo
```

小车输出自己的位置、朝向、速度。

### 3.10 相机数据查看

话题名由 world 文件决定。用 `ros2 topic list -t` 查实际名字。

看图像：

```bash
ros2 run rqt_image_view rqt_image_view
```

下拉框选图像话题，比如 `/demo_cam/camera1/image_raw`。

或用 RVIZ2 的 `Image` 显示类型。注意 QoS 要改成 `Best Effort`。

### 3.11 Gazebo 界面操作

| 操作 | 效果 |
|------|------|
| 鼠标左键拖动 | 旋转视角 |
| 鼠标右键拖动 | 平移视角 |
| 鼠标滚轮 | 缩放 |

Gazebo 界面是“上帝视角”，看整个场景。相机数据是“相机视角”，是相机拍到的。两者不同。

### 3.12 仿真时间

Gazebo 有自己的时钟，通过 `/clock` 话题发布。

节点可以选择：

- 用真实时间（默认）
- 用仿真时间（设置 `use_sim_time=true`）

用仿真时间的好处：仿真可以暂停、加速、慢放，节点跟着一起变。录 bag、做测试时有用。

### 3.13 常见易错点

| 现象 | 原因 | 解决 |
|------|------|------|
| Gazebo 开了但无话题 | 终端没 source | source 后重启 Gazebo |
| 只看到 `/parameter_events`、`/rosout` | `gazebo-plugins` 没装或没 source | 装 `ros-humble-gazebo-plugins`，source 后启动 |
| `gazebo` 命令找不到 | 本体没装 | `sudo apt install gazebo` |
| world 文件找不到 | 包没装 | `sudo apt install ros-humble-gazebo-plugins` |
| 相机话题名不是 `/camera/image_raw` | 每个 world 定义不同 | 用 `ros2 topic list -t` 查实际名字 |
| Ctrl+C 停不掉 Gazebo | 焦点在 Gazebo 窗口 | 点 Gazebo 终端，再 Ctrl+C；或 `pkill -f gazebo` |

### 3.14 从仿真到真机

ROS2 的设计目标之一：**代码不用改**。

控制节点订阅 `/cmd_vel`，发速度指令。

- 真机上，`/cmd_vel` 直接连电机
- Gazebo 里，`/cmd_vel` 通过 `gazebo_ros_diff_drive` 插件连仿真电机

节点代码完全一样，只换“数据源”和“执行器”。

### 3.15 Gazebo 版本和 ROS2 版本对应

| ROS2 版本 | Gazebo 版本 | 启动命令 |
|-----------|-------------|----------|
| Humble | Gazebo Classic 11 | `gazebo` |
| Jazzy 及以后 | 新 Gazebo | `gz sim` |

## 四、三者的关系

| 工具 | 角色 | 一句话 |
|------|------|--------|
| Gazebo | 造数据 | 不搬数据，只生产 |
| RVIZ2 | 看数据 | 不生产数据，只搬运 |
| RQT | 调系统 | 图形化调试工具集 |

典型工作流：

```
Gazebo 产生数据
    ↓
话题传输
    ↓
你的 ROS2 节点处理
    ↓
RVIZ2 显示效果
    ↓
RQT 调参数、看曲线
    ↓
rosbag 录制数据
```