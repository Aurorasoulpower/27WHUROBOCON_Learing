---
created: 2026-10-02
type: Note
tags:
  - "#ros2"
  - "#colcon"
---
# ROS2 构建系统、构建工具与 colcon 笔记

## 一、构建系统 vs 构建工具

```text
构建系统：编译单个包
构建工具：按依赖顺序调用构建系统，编译多个包
```

| 项目 | 构建系统 | 构建工具 |
|---|---|---|
| 作用对象 | 单个包 | 多个包 |
| 核心职责 | 定义如何编译一个包 | 按依赖顺序调度构建 |
| 代表 | CMake、ament_cmake、catkin、setuptools | colcon、catkin_make、catkin_tools |
| 关系 | 被调用者 | 调用者 |

```text
colcon（构建工具）
    ↓ 调用
CMake / Python setuptools（构建系统）
    ↓ 编译
单个功能包
```

ROS2 里常用：

```text
构建工具：colcon
构建系统：ament_cmake（C++）、setuptools（Python）
```

---

## 二、colcon build 进阶

### 总览
```text
colcon build
    ↓
① 选包      → 只编哪些
② 控目录    → 编到哪、怎么装
③ 控行为    → 线程、日志、错误处理
④ 传参数    → 给 CMake 传自定义参数
```

### 1. 选择编译哪些包

`--packages-select`：只编译指定包，不编依赖，也不编使用者。

```bash
colcon build --packages-select example_cpp
# 只编译 example_cpp 这一个包
```

`--packages-up-to`：编译指定包 + 它的依赖，方向向下。

```bash
colcon build --packages-up-to example_cpp
# 编译 example_cpp + 它的所有依赖
```

`--packages-above`：编译指定包 + 依赖它的包，方向向上。

```bash
colcon build --packages-above example_cpp
# 编译 example_cpp + 所有依赖它的包（递归）
```

| 参数 | 包含自己 | 包含依赖 | 包含使用者 | 方向 |
|---|---|---|---|---|
| `--packages-select` | ✅ | ❌ | ❌ | 只要自己 |
| `--packages-up-to` | ✅ | ✅ | ❌ | 向下 |
| `--packages-above` | ✅ | ❌ | ✅ | 向上 |

```text
A（底层）← B ← C（顶层）
--packages-select B   → 只编 B
--packages-up-to B    → 编 A、B
--packages-above B    → 编 B、C
```

### 2. 指定构建 / 安装目录

```bash
colcon build --build-base my_build --install-base my_install
# --build-base    指定中间文件目录，默认 build/
# --install-base  指定安装目录，默认 install/
```

### 3. 合并安装目录

```bash
colcon build --merge-install
# 所有包共用一个安装前缀，环境变量路径更短，包多时强烈建议加。
```

| 模式 | install 结构 | 环境变量 |
|---|---|---|
| 默认 | install/包A/、install/包B/… | 每个包一条路径，非常长 |
| `--merge-install` | install/ 下所有包混在一起 | 路径大部分相同，短 |

```text
默认：
install/
├── example_cpp/
├── example_py/
└── rclcpp/

--merge-install：
install/
├── bin/
├── lib/
├── share/
└── ...
```

### 4. 符号链接安装
```bash
colcon build --symlink-install
# install/ 里是符号链接，指向源码，不再拷贝文件
```

`colcon build` 默认会把源码文件复制到 ` install/ ` 目录。
加 `--symlink-install` 后，install/ 里不再拷贝，而是创建符号链接，指向 src/ 里的源码。

**好处**：修改 Python、launch、yaml、urdf 后，不用重新 colcon build，直接重启节点即可生效。

| 语言 / 文件 | 改代码后 |
|---|---|
| Python | 不用重新 build，直接重启节点即可 |
| C++ | 仍然要重新 build |
| launch / yaml / urdf | 不用重新 build |

Python 包、配置文件开发时必加。**C++ 不受益，因为二进制必须重编。**

### 5. 出错继续
```bash
colcon build --continue-on-error
# 某个包报错，继续编译其他包
```
不加的话，一个包报错，整体停止。

### 6. 控制构建线程
```bash
colcon build --executor sequential
# 一次只处理一个包，串行

colcon build --executor parallel
# 多个包并行处理（默认）

colcon build --parallel-workers 4
# 并行处理的最大作业数，默认 = os.cpu_count()
```
机器内存小就调小并行数，比如 `--parallel-workers 2`。

查看可用执行器
```bash
colcon extensions colcon_core.executor --verbose
# 列出 colcon 支持的所有执行器
```
### 7. 构建日志级别

```bash
colcon build --log-level info
# 控制 colcon 自身日志详细程度，不影响包内部编译输出
```
级别从低到高
```text
debug < info < warn < error < fatal
```

### 8. 传 CMake 参数
```bash
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
# 把 -DCMAKE_BUILD_TYPE=Release 直接传给 CMake

colcon build --cmake-args -DCMAKE_BUILD_TYPE=Debug
# Debug 模式，带调试符号

colcon build --cmake-args -DCMAKE_CXX_STANDARD=17
# 设置 C++ 标准

colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
# 传多个参数
```
和其他 colcon 选项混用时，参数前加空格分隔。

---

## 三、核心速查

```bash
# 选包
--packages-select 包名      # 只要它
--packages-up-to 包名       # 它 + 依赖
--packages-above 包名       # 它 + 使用者

# 目录
--build-base 目录           # 中间文件目录
--install-base 目录         # 安装目录
--merge-install             # 合并安装，环境变量短
--symlink-install           # 符号链接，Python 友好

# 行为
--continue-on-error         # 出错继续
--executor sequential       # 串行
--executor parallel         # 并行（默认）
--parallel-workers N        # 并行数，默认 CPU 核数
--log-level info            # colcon 日志级别

# 传参
--cmake-args -DKEY=VAL      # 传给 CMake
```
