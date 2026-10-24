---
created: 2026-10-05
type: Note
tags:
  - "#ros2"
  - "#节点通信"
---
## 一、参数是什么

参数是节点的一个配置值，本质是键值对。

**四个特点**

- 属于节点局部配置，不是全局
- 名字是字符串，值受类型限制
- 运行时动态生效，节点重启后丢失（除非保存/加载）
- 不支持自定义接口

**和其他通信机制的区别**

| 机制 | 角色 | 例子 |
|------|------|------|
| 话题 | 传感器数据、实时控制指令 | 激光数据、`cmd_vel` |
| 服务 | 查询状态、切换模式 | 查询电池、切模式 |
| 参数 | 配置值、阈值、增益 | PID 增益、速度上限、设备 IP |
| 动作 | 长任务闭环 | 导航、抓取 |

一句话：参数适合低频修改的配置值，不适合高频变化的控制量。

## 二、参数值类型

| 类型 | 说明 | 典型用途 |
|------|------|----------|
| `bool` / `bool[]` | 布尔 | 开关 |
| `int64` / `int64[]` | 整数 | 周期、数量、阈值 |
| `float64` / `float64[]` | 浮点 | PID 增益、速度上限 |
| `string` / `string[]` | 字符串 | IP、设备名、模式名 |
| `byte[]` | 字节数组 | 图片、点云 |

注意：整数只有 `int64`，浮点只有 `float64`，没有其他位宽。

---

## 三、CLI 命令

### 3.1 `ros2 param list`：列出节点所有参数

**作用**
列出当前系统中所有节点及其参数名。
```bash
# 基本用法
ros2 param list

# 示例输出
# /turtlesim:
#   background_b
#   background_g
#   background_r
#   use_sim_time
# /teleop_turtle:
#   scale_angular
#   scale_linear
#   use_sim_time

# 指定节点查看
ros2 param list /turtlesim

# 常用选项
ros2 param list -t    # 显示参数类型（部分版本支持）
ros2 param list -v    # 显示详细信息
```

从输出可以读出三件事：

- 参数挂在节点下面，是节点局部配置
- `/turtlesim` 有 `background_b/g/r` 三个参数，对应背景色的蓝、绿、红分量
- `use_sim_time` 是每个节点都有的内置参数

---

### 3.2 `ros2 param describe`：查看参数详细描述

**作用**
查看某个参数的类型、描述、约束、最大值、最小值。

```bash
# 基本用法
ros2 param describe <node_name> <param_name>

# 示例
ros2 param describe /turtlesim background_b

# 输出示例
# Parameter name: background_b
#   Type: integer
#   Description: Blue channel of the background color
#   Constraints:
#     Min value: 0
#     Max value: 255
#     Step: 1
```

**什么时候用**

- 看不懂参数名时
- 不确定取值范围时
- 不确定类型时
- 写代码前想确认参数接口时

---

### 3.3 `ros2 param get`：获取参数值

**作用**
获取指定节点指定参数的当前值。

```bash
# 基本用法
ros2 param get <node_name> <param_name>

# 示例
ros2 param get /turtlesim background_b

# 输出示例
# Integer value is: 255

# 再查红色和绿色
ros2 param get /turtlesim background_r
ros2 param get /turtlesim background_g

# 输出分别是 255、86、69，这就是默认蓝色的 RGB 组成
```

**输出格式**
不同类型参数输出前缀不同：

| 类型 | 输出前缀 |
|------|----------|
| `bool` | `Boolean value is:` |
| `int64` | `Integer value is:` |
| `float64` | `Double value is:` |
| `string` | `String value is:` |
| 数组 | `Integer[] value is:` 等 |

**注意事项**

- 节点名必须写全，带前导 `/`
- 参数名区分大小写
- 节点不在运行时命令会报错

---

### 3.4 `ros2 param set`：设置参数值

**作用**
临时修改指定节点指定参数的值。

```bash
# 基本用法
ros2 param set <node_name> <param_name> <value>

# 示例：把背景改成绿色（RGB 44, 156, 10）
ros2 param set /turtlesim background_r 44
ros2 param set /turtlesim background_g 156
ros2 param set /turtlesim background_b 10

# 成功输出
# Set parameter successful

# 失败输出示例
# Setting parameter failed: parameter 'background_x' not found
# Setting parameter failed: value must be an integer

# 数组类型设置
ros2 param set /node_name array_param "[1, 2, 3]"
```

**注意事项**

- 修改是临时的，节点重启后恢复默认值
- 值必须符合参数类型，`int64` 参数不能传浮点
- 节点必须正在运行
- 参数名必须已存在，不能凭空创建
- YAML 格式中冒号后必须有空格：`key: value`，不是 `key:value`

---

### 3.5 `ros2 param dump`：导出参数为 YAML

**作用**
把指定节点的当前所有参数值拍一张快照，导出成 YAML 格式。

```bash
# 基本用法
ros2 param dump <node_name>

# 示例
ros2 param dump /turtlesim

# 保存到文件（Humble 及之后需重定向）
ros2 param dump /turtlesim > turtlesim.yaml

# 查看内容
cat ./turtlesim.yaml

# 输出示例
# /turtlesim:
#   ros__parameters:
#     background_b: 10
#     background_g: 156
#     background_r: 44
#     use_sim_time: false
```

**版本差异**

| 版本 | 默认行为 |
|------|----------|
| Humble 及之后 | 默认打印到终端，不自动保存文件 |
| Humble 之前 | 部分版本自动保存为 `<node_name>.yaml` |

**YAML 结构说明**

- 第一层是节点名 `/turtlesim`
- 第二层固定是 `ros__parameters`
- 下面才是参数名和值

---

### 3.6 `ros2 param load`：从 YAML 恢复参数

**作用**
从 YAML 文件读取参数并设置到指定节点。

```bash
# 基本用法
ros2 param load <node_name> <file_name>

# 示例：先关闭再重新运行模拟器，然后加载
ros2 param load /turtlesim ./turtlesim.yaml

# 成功输出
# Set parameter background_b successful
# Set parameter background_g successful
# Set parameter background_r successful
# Set parameter use_sim_time successful
```

**注意事项**

- 节点必须在运行中
- YAML 文件中的节点名要和命令行指定的节点名一致
- 文件格式必须是合法 YAML
- 加载后参数只在内存生效，重启仍会丢失

---

### 3.7 `ros2 run --ros-args --params-file`：启动时加载参数

**作用**

让节点一启动就使用指定参数文件，避免每次手动 `load`。

```bash
# 基本用法
ros2 run <package_name> <executable_name> --ros-args --params-file <file_name>

# 示例
ros2 run turtlesim turtlesim_node --ros-args --params-file ./turtlesim.yaml

# 和其他 --ros-args 选项组合
ros2 run my_pkg my_node --ros-args \
  --params-file ./config/params.yaml \
  -r __node:=my_node_renamed \
  -p some_param:=42
```

常见组合：

| 选项 | 作用 |
|------|------|
| `--params-file <file>` | 加载参数文件 |
| `-p <name>:=<value>` | 直接设置单个参数 |
| `-r <from>:=<to>` | 重映射话题/节点名 |
| `--log-level <level>` | 设置日志级别 |

**注意事项**

- `--ros-args` 必须放在可执行名之后
- `--params-file` 之后的参数属于 `--ros-args` 范围
- YAML 中的节点名必须和实际节点名一致，否则参数不会生效

---

### 3.8 启动文件中加载参数

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            parameters=['./config/turtlesim.yaml']
        )
    ])
```

工程中这是最常用的方式，参数文件随包分发，启动时自动加载。

---

## 五、参数事件 QoS 预设

| 预设 | History/Depth | Reliability | Durability |
|------|---------------|-------------|------------|
| `qos_profile_parameters` | Keep last / 1000 | Reliable | Volatile |

Depth 大是因为参数变化事件不能丢。


## 六、常见坑速查

| 问题 | 原因 | 解决 |
|------|------|------|
| `set` 后重启节点值恢复 | 参数修改是临时的 | 用 `dump` 保存，`load` 或 `--params-file` 加载 |
| `dump` 后没看到文件 | Humble 及之后默认打印到终端 | 用 `>` 重定向到文件 |
| YAML 格式报错 | 冒号后缺空格 | 写成 `key: value` |
| 想看参数接口定义 | 参数不支持自定义接口 | 用 `ros2 interface show` 查消息接口 |
| `set` 时类型不匹配 | 参数值类型固定 | 先 `ros2 param get` 或 `describe` 确认类型 |
| `load` 后参数没生效 | YAML 中节点名与实际不符 | 检查 YAML 第一层节点名 |
| 参数名不存在 | 节点没声明该参数 | 参数必须先在代码里声明 |

