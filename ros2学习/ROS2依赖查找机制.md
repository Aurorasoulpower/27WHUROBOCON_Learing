---
created: 2026-09-30
type: Note
tags:
  - "#ros2"
---
# 编译语言链接方式
程序编译一般需要经**预处理、编译、汇编和链接**几个步骤。在实际应用中，有些公共代码需要反复使用，就把这些代码编译成为“库”文件。
在链接步骤中，链接器将从库文件取得所需的代码，复制到生成的可执行文件中，这种库称为静态（链接）库，其特点是可执行文件中包含了库代码的一份完整拷贝，缺点是被多次使用就会多份冗余拷贝。
还有一种库，就是程序在开始运行后调用库函数时才被载入，这种库独立于现有的程序，其本身不可执行，但包含着程序需要调用的一些函数，这种库称为动态（链接）库（Dynamic Link Library）。
- 在widows平台下，静态链接库是.lib文件，动态库文件是.dll文件。
- 在linux平台下，静态链接库是.a文件，动态链接库是.so文件。
```txt
源代码 .cpp
   ↓
预处理
   ↓
预处理后的代码
   ↓
编译
   ↓
汇编代码 .s
   ↓
汇编
   ↓
目标文件 .o
   ↓
链接
   ↓
可执行文件
```
- 预处理 = 把源代码整理、展开成编译器真正要看的代码。
- 编译 = 把人类写的 C/C++ 翻译成 CPU 更容易理解的指令形式。
- 汇编=汇编器把汇编代码进一步变成机器码，并形成目标文件（Object File）。.o 已经包含机器指令了，但它通常还不能直接运行。
- 链接 = 把各个已经编译好的代码模块拼起来，并解决函数、变量之间的引用关系。
---

库最基本的意义：
把已经写好的、可以重复使用的代码打包起来。

静态链接的关键：
>链接的时候，把需要的库代码复制进最终的可执行文件。

动态链接的关键：
>要实际调用的时候才由操作系统找到动态库加载对应的函数并调用

---

# C++ 依赖寻找与编译工具

## 一、C++ 编译的基本流程
```text
.cpp 源文件
   ↓
预处理
   ↓
编译
   ↓
汇编
   ↓
.o 目标文件
   ↓
链接
   ↓
可执行文件
```

对于 ROS2 C++ 节点，本质上也是：
```text
first_ros2_node.cpp
        ↓
找到头文件
        ↓
编译
        ↓
找到库文件
        ↓
链接
        ↓
first_node
```

---

## 二、g++：手动告诉编译器依赖在哪里

最原始的方法是直接使用 `g++`。
例如：
```bash
g++ first_ros2_node.cpp \
  -I/opt/ros/humble/include/rclcpp/ \
  -I/opt/ros/humble/include/rcl/ \
  -L/opt/ros/humble/lib/ \
  -lrclcpp \
  -lrcutils \
  -o first_node
```
这里最重要的是三个参数：

| 参数 | 作用 |
| --- | --- |
| `-I` | 找头文件 |
| `-L` | 找库文件 |
| `-l` | 链接哪个库 |

### 1. `-I`
指定头文件搜索路径。
例如代码：
```cpp
#include "rclcpp/rclcpp.hpp"
```
编译器需要找到：
```text
/opt/ros/humble/include/rclcpp/rclcpp/rclcpp.hpp
```
因此需要：
```bash
-I/opt/ros/humble/include/rclcpp/
```

### 2. `-L`
指定库文件搜索路径。
例如：
```bash
-L/opt/ros/humble/lib/
```
告诉链接器：
> 去这个目录寻找库。

### 3. `-l`
指定要链接的库。
```bash
-lrclcpp
```
实际寻找的文件通常类似：
```text
librclcpp.so
```
因此：
```text
-lrclcpp
        ↓
librclcpp.so
```

---

## 三、报错认识
### 1. `No such file or directory`
例如：
```text
fatal error: xxx.h: No such file or directory
```
通常是：
```text
编译阶段
↓
找不到头文件
↓
检查 -I
```

也就是：
```text
-I → 头文件搜索
```

### 2. `undefined reference to ...`
例如：
```text
undefined reference to ...
```

通常是：
```text
编译已经通过
↓
链接阶段失败
↓
检查库路径和链接库
```

重点检查：
```text
-L → 库在哪里
-l → 链接哪个库
```

---

## 四、Make：把 g++ 命令交给 Make 管理

如果每次都手写一大串 `g++` 很麻烦，可以写 `Makefile`。
例如：

```makefile
build:
	g++ first_ros2_node.cpp \
	-I/opt/ros/humble/include/rclcpp/ \
	-I/opt/ros/humble/include/rcl/ \
	-L/opt/ros/humble/lib/ \
	-lrclcpp -lrcutils \
	-o first_node

clean:
	rm -f first_node
```

以后：
```bash
make build
```
就相当于执行那一长串 `g++`。

### Makefile 的核心概念

```makefile
目标:
	命令
```

上面的示例中：

| 内容 | 含义 |
| --- | --- |
| `build` | target（目标） |
| `g++ ...` | recipe（执行的命令） |

> **命令前必须是真正的 TAB，不能是空格。**

---

## 五、CMake：让 CMake 自动生成 Makefile

Makefile 虽然方便，但我们还是需要自己维护大量 `g++` 参数。
于是进一步使用 `CMake`。

CMake 的核心作用：
```text
CMakeLists.txt
       ↓
    cmake ..
       ↓
自动生成 Makefile
       ↓
      make
       ↓
  编译程序
```
因此：
> **CMake 本身主要负责生成构建系统，而不是直接代替编译器。**

---

## 六、CMakeLists.txt

最开始我们手动写了大量：
```cmake
cmake_minimum_required(VERSION 3.22)

project(first_node)

#include_directories 添加特定的头文件搜索路径 ，相当于指定g++编译器的-I参数
include_directories(/opt/ros/humble/include/rclcpp/)
include_directories(/opt/ros/humble/include/rcl/)
include_directories(/opt/ros/humble/include/rcutils/)
include_directories(/opt/ros/humble/include/rcl_yaml_param_parser/)
include_directories(/opt/ros/humble/include/rosidl_runtime_c/)
include_directories(/opt/ros/humble/include/rosidl_typesupport_interface/)
include_directories(/opt/ros/humble/include/rcpputils/)
include_directories(/opt/ros/humble/include/builtin_interfaces/)
include_directories(/opt/ros/humble/include/rmw/)
include_directories(/opt/ros/humble/include/rosidl_runtime_cpp/)
include_directories(/opt/ros/humble/include/tracetools/)
include_directories(/opt/ros/humble/include/rcl_interfaces/)
include_directories(/opt/ros/humble/include/libstatistics_collector/)
include_directories(/opt/ros/humble/include/statistics_msgs/)

# link_directories - 向工程添加多个特定的库文件搜索路径，相当于指定g++编译器的-L参数
link_directories(/opt/ros/humble/lib/)

# add_executable - 生成first_node可执行文件
add_executable(first_node first_ros2_node.cpp)

# target_link_libraries - 为first_node(目标) 添加需要动态链接库，相同于指定g++编译器-l参数
# 下面的语句代替 -lrclcpp -lrcutils
target_link_libraries(first_node rclcpp rcutils)
```
这些实际上就是把之前的 `-I`、`-L` 搬到了 CMake 中。

对应关系：

| g++       | CMake                     | 作用          |
| --------- | ------------------------- | ----------- |
| `-I/path` | `include_directories()`   | 添加头文件路径     |
| `-L/path` | `link_directories()`      | 告知链接库位置     |
| `-lxxx`   | `target_link_libraries()` | 告知具体链接库     |
| `-o xxx`  | `add_executable()`        | 命名生成的.out文件 |

---

## 七、find_package：真正的简化

手动指定几十个依赖路径显然很麻烦。
ROS2 中更常见的方式是：
```cmake
cmake_minimum_required(VERSION 3.22)

project(first_node)

find_package(rclcpp REQUIRED)

add_executable(first_node first_ros2_node.cpp)

target_link_libraries(first_node rclcpp::rclcpp)
```

这里最关键的是：
```cmake
find_package(rclcpp REQUIRED)
```

它的意思可以简单理解成：
> **告诉 CMake：我要使用 `rclcpp`，请你自己找到并加载它的配置信息。**

---

## 八、find_package 到底找什么？

CMake 并不是“凭空知道” `rclcpp` 在哪里。
ROS2 安装时已经提供了 CMake 配置文件。
例如：
```text
/opt/ros/humble/share/rclcpp/cmake/rclcppConfig.cmake
```

因此：
```text
find_package(rclcpp REQUIRED)
              ↓
寻找 rclcpp 的 CMake 配置
              ↓
rclcppConfig.cmake
              ↓
加载 rclcpp 的编译/链接信息
```

这个配置文件已经知道：
```text
rclcpp 的头文件在哪里
rclcpp 的库在哪里
rclcpp 依赖哪些其他库
rclcpp 提供哪些 CMake target
```

---

## 九、CMAKE_PREFIX_PATH

CMake 寻找软件包时会参考多个搜索路径。
其中 ROS2 环境下非常重要的是：
```bash
echo $CMAKE_PREFIX_PATH
```
通常会包含：
```text
/opt/ros/humble
```
可以把它理解成：
> **告诉 CMake：ROS2 软件包主要安装在这个前缀目录下面。**
然后 CMake 可以进一步寻找：
```text
/opt/ros/humble/share/rclcpp/cmake/
```
最终找到：
```text
rclcppConfig.cmake
```

---

## 十、PATH 和 CMAKE_PREFIX_PATH 不要混淆

这是一个容易搞混的地方。
### PATH
```bash
echo $PATH
```

主要用于：
> **寻找可执行程序**

例如：
```bash
which ros2
```

可能得到：
```text
/opt/ros/humble/bin/ros2
```

### CMAKE_PREFIX_PATH
```bash
echo $CMAKE_PREFIX_PATH
```

主要用于：

> **帮助 CMake 寻找已经安装的软件包**
例如：
```text
/opt/ros/humble
```

然后进一步寻找：
```text
share/rclcpp/cmake/rclcppConfig.cmake
```

所以简单记：
```text
PATH
↓
找“程序”

CMAKE_PREFIX_PATH
↓
帮助 CMake 找“软件包”
```

---

## 十一、rclcpp::rclcpp 是什么？

这一句：
```cmake
target_link_libraries(first_node rclcpp::rclcpp)
```
中的：
```text
rclcpp::rclcpp
```

可以暂时理解为：
> **rclcpp 已经为我们准备好的 CMake target。**

它不是单纯告诉 CMake：
```text
“去找一个叫 librclcpp.so 的文件”
```

而是使用 `rclcpp` 包已经配置好的目标。
因此：
```text
find_package(rclcpp REQUIRED)
             ↓
找到并加载 rclcpp
             ↓
rclcpp::rclcpp
             ↓
使用 rclcpp 提供的配置和依赖
```

---

## 十二、三种编译方式的演进
我们实际上完整经历了三种方式。
### ① 直接 g++
```text
自己寻找所有依赖
自己写 -I
自己写 -L
自己写 -l
自己指定输出
```
↓
### ② Make
```text
把 g++ 命令写进 Makefile
```
以后：
```bash
make build
```
↓
### ③ CMake
```text
CMakeLists.txt
      ↓
find_package()
      ↓
cmake ..
      ↓
自动生成 Makefile
      ↓
make
```

```text
g++
 ↑
真正负责编译和链接


Make
 ↑
管理编译命令


CMake
 ↑
生成/管理构建系统
```


## 附：速查表

| 场景 | 重点检查 |
| --- | --- |
| `No such file or directory` | `-I`、头文件搜索路径 |
| `undefined reference to ...` | `-L`、`-l`、链接库 |
| CMake 找不到包 | `CMAKE_PREFIX_PATH`、`xxxConfig.cmake` |
| 找可执行程序 | `PATH` |
| 帮助 CMake 找软件包 | `CMAKE_PREFIX_PATH` |
| 现代 CMake 链接库 | `find_package(xxx)` + `xxx::xxx` |

---



# Python 寻找依赖及setup打包

## 1. Python 依赖查找

```text
Python代码
   ↓
import xxx
   ↓
Python 搜索模块路径
   ↓
找到 xxx → 正常导入
找不到 → ModuleNotFoundError
```

### PYTHONPATH

```bash
echo $PYTHONPATH
```

查看 Python 额外的模块搜索路径。

例如 ROS2：

```text
/opt/ros/humble/lib/python3.10/site-packages
/opt/ros/humble/local/lib/python3.10/dist-packages
```

`rclpy` 实际位于：

```text
/opt/ros/humble/local/lib/python3.10/dist-packages/rclpy
```

所以：

```bash
python3 -c "import rclpy; print(rclpy.__file__)"
```

可以查看 Python 实际加载的 `rclpy`。

### 常见错误

```text
ModuleNotFoundError: No module named 'xxx'
```

含义：

> Python 当前搜索路径中找不到 `xxx`。

可以检查：

```bash
echo $PYTHONPATH
```

以及：

```bash
find /opt/ros/humble -name "xxx"
```

ROS2 环境变量异常时通常可以：

```bash
source /opt/ros/humble/setup.bash
```

恢复 ROS2 环境。

---

## 2. Python 与 C++ 依赖查找对比

| C++ | Python |
| --- | --- |
| `#include "xxx.h"` | `import xxx` |
| `-I` / CMake | `PYTHONPATH` |
| 寻找头文件 | 寻找 Python 模块 |
| 找不到 → 编译错误 | 找不到 → `ModuleNotFoundError` |

核心记忆：

```text
C++：-I        → 找头文件
Python：PYTHONPATH → 找模块
```

---

## 3. Python 打包

### 为什么需要打包？

把一个 Python 项目整理成：

```text
可以安装
可以分发
可以被其他人直接使用
```

例如：

```bash
pip install .
```

---

## 4. setup.py

`setup.py` 是 Python 项目的**安装/分发配置文件**。

例如：

```python
from setuptools import setup, find_packages

setup(
    name="mytest",
    version="1.0",
    packages=find_packages()
)
```

告诉打包工具：

```text
项目叫什么
版本是多少
哪些 Python 包需要被打包
```

---

## 5. setuptools

```text
setuptools
    ↓
Python 常用打包工具
    ↓
读取 setup.py
    ↓
完成 Python 项目的构建、安装、分发
```

### find_packages()

```python
packages=find_packages()
```

自动寻找项目中的 Python package。

通常会寻找包含：

```text
__init__.py
```

的包目录。

---

## 6. 最重要的区别

一定不要把这两个东西混为一谈：

```text
PYTHONPATH
    ↓
解决“Python 去哪里找模块”
```

```text
setup.py
    ↓
解决“这个 Python 项目怎么打包、安装、分发”
```

所以：

```text
import rclpy
    ↓
PYTHONPATH
    ↓
找到 rclpy
```

而：

```text
pip install .
    ↓
setup.py / setuptools
    ↓
安装这个 Python 项目
```

---

## 7. 和 ROS2 联系起来

以后 ROS2 Python 包经常会看到：

```text
my_robot/
├── package.xml
├── setup.py
├── setup.cfg
└── my_robot/
    ├── __init__.py
    └── node.py
```

目前知道这些文件**分别负责什么**即可，不需要背 `setup()` 那几十个参数。

---

## 一句话总结

```text
Python：

import
  ↓
Python 搜索路径
  ↓
PYTHONPATH
  ↓
找到模块


Python 项目：
setup.py
  ↓
setuptools
  ↓
打包 / 安装 / 分发
```
