---
created: 2026-10-02
type: Note
tags:
  - "#ros2"
  - "#colcon"
---

## 一、基本层级

```text
Workspace 工作空间
    ↓
Package 功能包
    ↓
Executable 可执行程序
    ↓
Node 节点
```

一个工作空间可含多个功能包。  
一个功能包可含多个可执行程序、多个节点。

典型结构：

```text
robot_ws/
├── src/              # 源代码
│   ├── vision_pkg/
│   └── lidar_pkg/
├── build/            # 编译中间文件
├── install/          # 编译安装结果
└── log/              # 编译日志
```

---

## 二、工作空间 Workspace

作用：组织 ROS2 功能包的目录。
创建：
```bash
mkdir -p robot_ws/src
cd robot_ws
```
`src` 用来存放自己编写或下载的 ROS2 功能包。

---

## 三、功能包 Package

功能包是 ROS2 管理代码的基本单位。
常见内容：
```text
功能包
├── 源代码
├── package.xml
├── setup.py              # Python 包常见
└── CMakeLists.txt        # C++ 包常见
```

常见构建类型：
```text
ament_python    → Python
ament_cmake     → C++
```

---

## 四、如何获得功能包

### 1. apt 安装（作者已编译完成，可直接使用）
```bash
sudo apt install ros-humble-包名
```

例如：
```bash
sudo apt install ros-humble-turtlesim
```

### 2. 源码编译

源码放入：
```text
robot_ws/src/
```

然后：
```bash
cd robot_ws
colcon build
source install/setup.bash
```
`source` 后，当前终端才能识别该工作空间中的包。

---

## 五、ros2 pkg 常用命令

### 创建功能包
```bash
ros2 pkg create <package-name> \
--build-type <ament_python|ament_cmake> \
--dependencies <依赖>
```

示例：
```bash
ros2 pkg create vision_pkg \
--build-type ament_python \
--dependencies rclpy
```

### 查看所有功能包
```bash
ros2 pkg list
```

### 查看某个包的可执行程序
```bash
ros2 pkg executables <package-name>

#示例
ros2 pkg executables turtlesim
```

作用：直接给出 `包名 + 可执行程序名`。

### 查看包安装位置
```bash
ros2 pkg prefix <package-name>

#示例
ros2 pkg prefix turtlesim
# /opt/ros/humble
```

### 查看 package.xml 信息
```bash
ros2 pkg xml <package-name>
```

可查看：包名、版本、描述、维护者、许可证、依赖关系等。

---

## 六、package.xml

作用：功能包的“身份证”和说明书。
记录：
```text
包叫什么
版本是多少
谁维护
干什么
依赖哪些包
使用什么构建工具
```
示例：
```xml
<name>vision_pkg</name>

<depend>rclpy</depend>
<depend>sensor_msgs</depend>
```
ROS2 根据这些信息处理依赖和构建关系。

---

## 七、Colcon

Colcon 是 ROS2 常用的工作空间构建工具。
流程：
```text
源码
 ↓
colcon build
 ↓
编译 / 安装
 ↓
ROS2 可以运行
```
安装：
```bash
sudo apt install python3-colcon-common-extensions
```

---

## 八、colcon build 后的三个目录

```text
robot_ws/
├── src/
├── build/
├── install/
└── log/
```

| 目录 | 作用 |
|---|---|
| `build/` | 编译中间文件，一般不用直接改 |
| `install/` | 最终安装结果，运行源码编译包主要依赖这里 |
| `log/` | 编译、测试日志，出问题看这里 |

编译后通常需要：
```bash
source install/setup.bash
```

---

## 九、Colcon 常用命令
进阶使用见[[ROS2 Colcon进阶]]
```bash
# 编译整个工作空间
colcon build

# 只编译指定功能包
colcon build --packages-select <package-name>

# 指定包 + 不编译测试
colcon build \
--packages-select vision_pkg \
--cmake-args -DBUILD_TESTING=0

# 运行测试
colcon test

# 开发阶段推荐
colcon build --symlink-install
```

`--symlink-install` 作用：安装目录通过软链接关联源码。  
Python 项目尤其方便，修改源码后少重新安装。

---

## 十、Python 文件 ≠ 可执行程序

真正的 ROS2 可执行程序名，要看 `setup.py`：

```python
entry_points={
    'console_scripts': [
        'publisher_member_function_with_wait_for_all_acked = examples_rclpy_minimal_publisher.publisher_member_function_with_wait_for_all_acked:main'
    ],
}
```

对应结果：
```text
包名：
examples_rclpy_minimal_publisher

可执行程序：
publisher_member_function_with_wait_for_all_acked
```

运行：
```bash
ros2 run examples_rclpy_minimal_publisher \
publisher_member_function_with_wait_for_all_acked
```

---

## 十一、如何快速确认可执行程序

不要猜，直接查：
```bash
ros2 pkg executables <package-name>

#示例：
ros2 pkg executables examples_rclpy_minimal_publisher
```

输出类似：
```text
examples_rclpy_minimal_publisher publisher_member_function
examples_rclpy_minimal_publisher publisher_member_function_with_wait_for_all_acked
```
然后运行：
```bash
ros2 run examples_rclpy_minimal_publisher \
publisher_member_function_with_wait_for_all_acked
```

---

## 十二、完整 ROS2 开发流程

```text
① 创建工作空间
        ↓
② 在 src 中创建 / 下载功能包
        ↓
③ 编写节点
        ↓
④ colcon build
        ↓
⑤ source install/setup.bash
        ↓
⑥ ros2 run 包名 可执行程序
        ↓
⑦ 测试 ROS2 通信
        ↓
⑧ 修改代码
        ↓
⑨ 重新 build
```

开发阶段推荐：

```bash
colcon build --symlink-install
```

