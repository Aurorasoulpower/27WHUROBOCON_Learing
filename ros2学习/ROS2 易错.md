---
created: 2026-10-05
type: Note
tags:
  - "#ros2"
---
# 工作空间 功能包 代码文件 可执行程序 节点

## 一、从大到小的层级关系

```
工作空间（workspace）
 └── src/
      └── 功能包（package）
           ├── 代码文件（source file）
           ├── 可执行程序（executable）
           └── 节点（node，运行时概念）
```

用你之前的实操举例：

| 层级 | 实际名字 | 所在位置或定义处 |
|------|----------|------------------|
| 工作空间 | `chapt4_ws` | `~/d2lros2/chapt4/chapt4_ws` |
| 功能包 | `example_param_rclpy` | `chapt4_ws/src/example_param_rclpy` |
| 代码文件 | `param_basic.py` | `src/example_param_rclpy/example_param_rclpy/param_basic.py` |
| 可执行程序 | `param_basic` | `setup.py` 的 `entry_points` 里注册 |
| 节点名 | `param_basic` | 代码里 `ParamBasicNode("param_basic")` 指定 |

---

## 二、逐个名词定义

### 2.1 工作空间（workspace）

- 一个目录，里面放 `src/`、`build/`、`install/`、`log/`。
- 是编译和运行的组织单位。
- 一个工作空间里可以有多个功能包。
- 你执行 `colcon build` 时，就是在工作空间根目录下执行。
- 例子：`~/d2lros2/chapt4/chapt4_ws`

### 2.2 功能包（package）

- ROS2 软件的基本组织单位。
- 放在工作空间的 `src/` 下。
- 包含代码、接口、配置、启动文件、`package.xml`、`setup.py` 或 `CMakeLists.txt`。
- 有唯一的名字，编译后可以用 `ros2 run <package_name> <executable_name>` 运行。
- 一个功能包可以定义多个可执行程序、多个节点。
- 例子：`example_param_rclpy`

### 2.3 代码文件（source file）

- 实际写代码的文件，比如 `.py`、`.cpp`。
- 放在功能包内部的源码目录里。
- Python 功能包的代码通常放在与包同名的子目录下。
- 例子：`src/example_param_rclpy/example_param_rclpy/param_basic.py`

### 2.4 可执行程序（executable）

- 用 `ros2 run` 时跟在功能包后面的那个名字。
- 它不是一个“文件”，而是一个“入口”。
- Python 功能包里，在 `setup.py` 的 `entry_points` 中注册：

```python
entry_points={
    'console_scripts': [
        'param_basic = example_param_rclpy.param_basic:main',
    ],
},
```

- 左边 `param_basic` 就是可执行程序名，右边指向代码文件里的 `main` 函数。
- C++ 功能包里，可执行程序是 `CMakeLists.txt` 里 `add_executable` 生成的二进制文件。
- 一个功能包可以有多个可执行程序。
- 例子：`param_basic`

### 2.5 节点（node）

- 运行时概念。节点是 ROS2 计算图里的一个参与者。
- 节点在代码里创建，比如 `node = ParamBasicNode("param_basic")`。
- 节点名是节点在 ROS2 图里的唯一标识，可以用 `ros2 node list` 看到。
- 节点名可以在代码里写死，也可以在启动时用重映射改：

```bash
ros2 run example_param_rclpy param_basic --ros-args -r __node:=my_node
```

- 一个可执行程序通常创建一个节点，但也可以创建多个节点。
- 例子：节点名 `param_basic`

---

## 三、用一条命令串起来

```bash
ros2 run example_param_rclpy param_basic --ros-args -p rcl_log_level:=10
```

| 命令部分 | 对应概念 | 说明 |
|----------|----------|------|
| `example_param_rclpy` | 功能包名 | 告诉 ROS2 去哪个包里找 |
| `param_basic` | 可执行程序名 | 告诉 ROS2 运行哪个入口 |
| `--ros-args` | 分隔符 | 后面的参数传给 ROS2 系统 |
| `-p rcl_log_level:=10` | 参数赋值 | 启动时把参数设为 10 |
| 运行后产生的节点名 | `param_basic` | 由代码里 `ParamBasicNode("param_basic")` 决定 |

---

## 四、容易混淆的几组概念

### 4.1 可执行程序 vs 代码文件

| 对比项 | 可执行程序 | 代码文件 |
|--------|------------|----------|
| 是什么 | 入口名，注册在 `setup.py` 或 CMake 里 | 实际写代码的 `.py` 或 `.cpp` 文件 |
| 用在哪 | `ros2 run` 的第二个参数 | 被可执行程序指向 |
| 能否重名 | 同一个功能包内不能重名 | 可以和其他包里的文件重名 |
| 例子 | `param_basic` | `param_basic.py` |

它们可以同名，也可以不同名。`setup.py` 里可以写：

```python
'my_executable = example_param_rclpy.param_basic:main'
```

这样可执行程序叫 `my_executable`，代码文件还是 `param_basic.py`。

### 4.2 可执行程序 vs 节点名

| 对比项 | 可执行程序 | 节点名 |
|--------|------------|--------|
| 是什么 | 启动入口 | 运行时在图里的名字 |
| 何时确定 | 编译前在 `setup.py`/CMake 里注册 | 运行时由代码或重映射决定 |
| 命令中位置 | `ros2 run <pkg> <exec>` 的第二个参数 | `ros2 node list` 看到的名字 |
| 能否改 | 改 `setup.py` 重新编译 | 启动时 `-r __node:=xxx` 即可改 |
| 例子 | `param_basic` | `param_basic` |

它们经常同名，但本质不同。可执行程序是“怎么启动”，节点名是“启动后叫什么”。

### 4.3 功能包 vs 工作空间

| 对比项 | 功能包 | 工作空间 |
|--------|--------|----------|
| 是什么 | 软件组织单位 | 编译和运行的组织单位 |
| 位置 | 工作空间的 `src/` 下 | 最外层目录 |
| 数量关系 | 一个工作空间可含多个功能包 | 一个工作空间只有一个 |
| 命令 | `ros2 pkg create` 创建 | `mkdir` 创建，`colcon build` 编译 |
| 例子 | `example_param_rclpy` | `chapt4_ws` |

### 4.4 节点 vs 功能包

| 对比项 | 节点 | 功能包 |
|--------|------|--------|
| 是什么 | 运行时参与者 | 代码组织单位 |
| 数量关系 | 一个功能包可定义多个节点 | 一个节点属于某个功能包 |
| 何时存在 | 节点运行时 | 编译前就存在 |
| 查看命令 | `ros2 node list` | `ros2 pkg list` |

---

## 五、完整对应关系图（以你的实操为例）

```
~/d2lros2/chapt4/chapt4_ws/          ← 工作空间
├── src/
│   └── example_param_rclpy/         ← 功能包
│       ├── example_param_rclpy/
│       │   └── param_basic.py       ← 代码文件
│       ├── setup.py                 ← 注册可执行程序
│       │     entry_points:
│       │       'param_basic = ...'  ← 可执行程序名
│       └── package.xml
└── install/

运行：
ros2 run example_param_rclpy param_basic
         └─功能包────────┘ └─可执行程序─┘
运行后：
ros2 node list
/param_basic                         ← 节点名
```

---

## 六、一句话区分

- **工作空间**：最大的目录，装功能包。
- **功能包**：装代码、接口、配置的组织单位。
- **代码文件**：实际写代码的 `.py` / `.cpp`。
- **可执行程序**：`ros2 run` 后面跟的入口名，在 `setup.py` 或 CMake 里注册。
- **节点**：运行起来的实例，有唯一的名字，是 ROS2 图里的参与者。

`ros2 run` 命令的两个参数分别是：功能包名、可执行程序名。运行后产生的节点名，由代码或重映射决定，和可执行程序名可以不同。

