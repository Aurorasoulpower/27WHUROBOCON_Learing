---
created: 2026-10-02
type: Note
tags:
  - "#ros2"
  - "#节点通信"
---


## 一、Python 版节点基础

### 1. 总览

```text
工作空间 chapt2_ws
    ↓
功能包 example_py
    ↓
节点文件 node_02.py
    ↓
入口配置 setup.py
    ↓
编译 colcon build
    ↓
运行 ros2 run example_py node_02
```

### 2. 创建功能包

#### 命令格式

```bash
ros2 pkg create 包名 --build-type ament_python --dependencies rclpy
```

#### 示例

```bash
cd ~/d2lros2/chapt2/chapt2_ws/src
ros2 pkg create example_py --build-type ament_python --dependencies rclpy
```

#### 命令解析

```text
example_py        # 包名，小写+下划线，不要用 .py
--build-type      # ament_python，Python 包编译类型
--dependencies    # rclpy，ROS2 Python 客户端库
```

#### 创建后目录

```text
example_py/
├── example_py/
│   └── __init__.py
├── package.xml
├── resource/
├── setup.cfg
├── setup.py
└── test/
```

### 3. 编写节点

#### 文件位置

```text
example_py/example_py/node_02.py
```

#### 代码

```python
import rclpy
from rclpy.node import Node

def main(args=None):
    rclpy.init(args=args)
    node = Node("node_02")
    node.get_logger().info("大家好，我是node_02.")
    rclpy.spin(node)
    rclpy.shutdown()
```

#### 逐行解析

```python
import rclpy                         # 导入 ROS2 Python 客户端库
from rclpy.node import Node          # 导入 Node 基类

def main(args=None):                 # 节点入口函数
    rclpy.init(args=args)            # 初始化 rclpy
    node = Node("node_02")           # 创建节点，节点名 /node_02
    node.get_logger().info("...")    # 打印 INFO 日志
    rclpy.spin(node)                 # 阻塞运行，等待 Ctrl+C
    rclpy.shutdown()                 # 退出后关闭 rclpy
```

#### 节点五步

| 步骤 | 代码 |
|---|---|
| 1. 导入库文件 | `import rclpy` |
| 2. 初始化客户端库 | `rclpy.init(args=args)` |
| 3. 新建节点对象 | `Node("node_02")` |
| 4. spin 循环节点 | `rclpy.spin(node)` |
| 5. 关闭客户端库 | `rclpy.shutdown()` |

### 4. 配置入口

#### 文件

```text
example_py/setup.py
```

#### 修改

```python
entry_points={
    'console_scripts': [
        "node_02 = example_py.node_02:main"
    ],
},
```

#### 解析

```text
node_02                     # ros2 run 的可执行名
example_py.node_02          # Python 包.模块
:main                       # 调用的函数
```

**可执行名不一定等于 .py 文件名，但此处保持一致。**

### 5. 编译运行

```bash
cd ~/d2lros2/chapt2/chapt2_ws
colcon build
source install/setup.bash
ros2 run example_py node_02
```

#### 输出

```text
[INFO] [时间] [node_02]: 大家好，我是node_02.
```

### 6. 验证

另开终端：

```bash
source install/setup.bash
ros2 node list
```

输出：

```text
/node_02
```

### 7. 核心速查

```bash
# 创建包
ros2 pkg create example_py --build-type ament_python --dependencies rclpy

# 节点文件
example_py/example_py/node_02.py

# setup.py 入口
"node_02 = example_py.node_02:main"

# 编译
colcon build

# source
source install/setup.bash

# 运行
ros2 run example_py node_02

# 验证
ros2 node list
```

### 8. 易错点

```text
包名不要带 .py
--build-type 不能拆成 --build -type
node_02.py 必须放在 example_py/example_py/ 下
setup.py 模块名写 node_02，不写 node_02.py
改 setup.py 后必须重新 colcon build
新终端必须 source install/setup.bash
```

---

## 二、C++ 版节点基础

### 1. 总览

```text
工作空间 chapt2_ws
    ↓
功能包 example_cpp
    ↓
节点文件 node_01.cpp
    ↓
入口配置 CMakeLists.txt
    ↓
编译 colcon build
    ↓
运行 ros2 run example_cpp node_01
```

### 2. 创建功能包

#### 命令格式

```bash
ros2 pkg create 包名 --build-type ament_cmake --dependencies rclcpp
```

#### 示例

```bash
cd ~/d2lros2/chapt2/chapt2_ws/src
ros2 pkg create example_cpp --build-type ament_cmake --dependencies rclcpp
```

#### 命令解析

```text
example_cpp       # 包名，小写+下划线
--build-type      # ament_cmake，C++ 包编译类型
--dependencies    # rclcpp，ROS2 C++ 客户端库
```

#### 创建后目录

```text
example_cpp/
├── CMakeLists.txt
├── include/example_cpp/
├── package.xml
└── src/
```

### 3. 编写节点

#### 文件位置

```text
example_cpp/src/node_01.cpp
```

#### 代码

```cpp
#include "rclcpp/rclcpp.hpp"

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<rclcpp::Node>("node_01");
    RCLCPP_INFO(node->get_logger(), "node_01节点已经启动.");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

#### 逐行解析

```cpp
#include "rclcpp/rclcpp.hpp"                     // 导入 ROS2 C++ 客户端库
rclcpp::init(argc, argv);                        // 初始化 rclcpp
auto node = std::make_shared<rclcpp::Node>("node_01"); // 创建节点，节点名 /node_01
RCLCPP_INFO(node->get_logger(), "...");          // 打印 INFO 日志
rclcpp::spin(node);                              // 阻塞运行，等待 Ctrl+C
rclcpp::shutdown();                              // 退出后关闭 rclcpp
return 0;                                        // 正常退出
```

#### 节点五步

| 步骤 | 代码 |
|---|---|
| 1. 导入库文件 | `#include "rclcpp/rclcpp.hpp"` |
| 2. 初始化客户端库 | `rclcpp::init(argc, argv);` |
| 3. 新建节点对象 | `std::make_shared<rclcpp::Node>("node_01")` |
| 4. spin 循环节点 | `rclcpp::spin(node);` |
| 5. 关闭客户端库 | `rclcpp::shutdown();` |

### 4. 配置入口

#### 文件

```text
example_cpp/CMakeLists.txt
```

#### 在文件末尾加入

```cmake
add_executable(node_01 src/node_01.cpp)
ament_target_dependencies(node_01 rclcpp)

install(TARGETS
  node_01
  DESTINATION lib/${PROJECT_NAME}
)
```

#### 解析

```cmake
add_executable(node_01 src/node_01.cpp)          # 编译 node_01.cpp 为可执行文件 node_01
ament_target_dependencies(node_01 rclcpp)        # 链接 rclcpp 依赖
install(TARGETS node_01 DESTINATION lib/${PROJECT_NAME}) # 安装到 install 目录
```

**三行缺一不可。**

### 5. 编译运行

```bash
cd ~/d2lros2/chapt2/chapt2_ws
colcon build
source install/setup.bash
ros2 run example_cpp node_01
```

#### 输出

```text
[INFO] [时间] [node_01]: node_01节点已经启动.
```

### 6. 验证

另开终端：

```bash
source install/setup.bash
ros2 node list
```

输出：

```text
/node_01
```

### 7. 改代码后怎么办

C++ 是编译型语言，改 `.cpp` 后必须：

```text
Ctrl+C 停止节点
    ↓
colcon build
    ↓
source install/setup.bash
    ↓
ros2 run example_cpp node_01
```

**不重新编译，跑的还是旧程序。**

### 8. 核心速查

```bash
# 创建包
ros2 pkg create example_cpp --build-type ament_cmake --dependencies rclcpp

# 节点文件
example_cpp/src/node_01.cpp

# CMakeLists.txt 末尾加
add_executable(node_01 src/node_01.cpp)
ament_target_dependencies(node_01 rclcpp)
install(TARGETS node_01 DESTINATION lib/${PROJECT_NAME})

# 编译
colcon build

# source
source install/setup.bash

# 运行
ros2 run example_cpp node_01

# 验证
ros2 node list
```

### 9. 易错点

```text
CMakeLists.txt 三行不能漏
源码路径写 src/node_01.cpp
改 .cpp 后必须重新 colcon build
新终端必须 source install/setup.bash
RCLCPP_INFO 里要传 node->get_logger()
make_shared 创建节点，用 -> 访问成员
```

---

## Python / C++ 速查对比

| 项目 | Python | C++ |
|---|---|---|
| 编译类型 | `ament_python` | `ament_cmake` |
| 依赖 | `rclpy` | `rclcpp` |
| 源码目录 | `example_py/example_py/` | `example_cpp/src/` |
| 节点文件 | `node_02.py` | `node_01.cpp` |
| 入口配置 | `setup.py` | `CMakeLists.txt` |
| 初始化 | `rclpy.init()` | `rclcpp::init(argc, argv)` |
| 创建节点 | `Node("node_02")` | `std::make_shared<rclcpp::Node>("node_01")` |
| 打日志 | `node.get_logger().info(...)` | `RCLCPP_INFO(node->get_logger(), ...)` |
| spin | `rclpy.spin(node)` | `rclcpp::spin(node)` |
| 关闭 | `rclpy.shutdown()` | `rclcpp::shutdown()` |
| 改代码后 | 通常不用重编，改 setup.py 要 | **必须重新编译** |
| 运行 | `ros2 run example_py node_02` | `ros2 run example_cpp node_01` |
| 验证 | `ros2 node list` → `/node_02` | `ros2 node list` → `/node_01` |

---
