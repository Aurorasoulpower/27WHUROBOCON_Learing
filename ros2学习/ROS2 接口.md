---
created: 2026-10-04
type: Note
tags:
  - "#ros2"
  - "#接口"
---
## 一、接口是什么

接口，英文 **Interface**，本质是一种 **规范**。
在 ROS2 中，接口是通信双方约定的数据格式，规定：

- 消息里有哪些字段；
- 每个字段是什么类型；
- 字段叫什么名字。

例如：
```text
std_msgs/msg/String
std_msgs/msg/UInt32
```
这些都是 ROS2 提前定义好的接口。

核心理解：
> 接口不是服务才有的。  
> 话题、服务、动作都有各自的接口。  
> 话题中的消息类型就是接口，叫消息接口。

---

## 二、为什么需要接口
### 1. 统一数据格式
不同厂家、不同设备、不同程序之间，如果数据格式不统一，就需要反复适配。
### 2. 跨语言、跨平台、跨设备
定义好接口后，ROS2 会生成不同语言的接口类：
- Python：`std_msgs.msg.String`
- C++：`std_msgs::msg::String`
只要接口相同，Python 节点和 C++ 节点就能互相通信。

---

## 三、ROS2 自带的接口

安装 ROS2 时，系统自带很多常用接口包。
常见接口包：

| 接口包 | 用途 |
|---|---|
| `std_msgs` | 标准消息类型，如 `String`、`Int32`、`Float64` |
| `sensor_msgs` | 传感器消息，如 `LaserScan`、`Image`、`Imu` |
| `geometry_msgs` | 几何消息，如 `Pose`、`Twist`、`Point` |
| `nav_msgs` | 导航消息，如 `Odometry`、`Path` |

---

## 四、接口的三种类型

ROS2 有四种通信方式：
- 话题 Topics
- 服务 Services
- 动作 Action
- 参数 Parameters

其中：
- **话题、服务、动作**支持自定义接口。
- 参数不支持自定义接口。

三种接口对应关系

| 通信方式 | 接口类型 | 文件后缀 |
|---|---|---|
| 话题 | 消息接口 | `.msg` |
| 服务 | 服务接口 | `.srv` |
| 动作 | 动作接口 | `.action` |

---

## 五、接口文件格式

### 1. 话题接口：`xxx.msg`

```text
int64 num
```

只有一部分，全是字段。

### 2. 服务接口：`xxx.srv`

```text
int64 a
int64 b
---
int64 sum
```

用 `---` 分隔：

- `---` 上面：请求字段。
- `---` 下面：响应字段。

### 3. 动作接口：`xxx.action`

```text
int32 order
---
int32[] sequence
---
int32[] partial_sequence
```

用两个 `---` 分隔成三部分：

- 第一部分：目标 Goal。
- 第二部分：结果 Result。
- 第三部分：反馈 Feedback。

---

## 六、接口数据类型

接口字段类型分两类。

### 1. 基础类型

| 类型 | 说明 |
|---|---|
| `bool` | 布尔 |
| `byte` | 字节 |
| `char` | 字符 |
| `float32`、`float64` | 浮点数 |
| `int8`、`uint8` | 8 位整数 |
| `int16`、`uint16` | 16 位整数 |
| `int32`、`uint32` | 32 位整数 |
| `int64`、`uint64` | 64 位整数 |
| `string` | 字符串 |

后面加 `[]` 表示数组：
```text
int32[] sequence
```

### 2. 包装类型

在已有接口类型上进行包含。
例如：
```text
uint32 id
string image_name
sensor_msgs/Image
```
这里 `sensor_msgs/Image` 是包装类型。  
你可以在自己的接口里嵌入其他接口。

### 3. 常量

接口文件里可以定义常量：
```text
uint32 STATUS_MOVEING = 1
uint32 STATUS_STOP = 2
uint32 status
float32 pose
```

- `STATUS_MOVEING = 1`、`STATUS_STOP = 2` 是常量。
- `status`、`pose` 是字段。

常量用于给字段提供可读取值（置标志位）。  
例如 `status == 1` 表示移动中，`status == 2` 表示停止。

---

## 七、接口如何生成代码

你只写变量类型和名称，程序里怎么用？

ROS2 的转换过程：
```text
msg、srv、action 文件
        │
        ▼
   ROS2 IDL 转换器
        │
        ▼
Python 的 .py 文件、C++ 的 .h 头文件
```

ROS2 的 IDL 模块把接口文件转换成不同语言的代码。  
有了这些代码，就可以在程序里导入并使用。

例如：

- Python：`from example_interfaces.srv import AddTwoInts`
- C++：`#include "example_interfaces/srv/add_two_ints.hpp"`
这就是接口能跨语言、跨平台、跨设备的原因。

---

## 八、接口核心规则

### 1. 同一通信必须使用相同接口

- 同一个话题，所有发布者和订阅者必须使用相同消息接口。
- 同一个服务，客户端和服务端必须使用相同服务接口。
- 同一个动作，客户端和服务端必须使用相同动作接口。

如果接口不一致，通信无法正常建立或无法正确解析。

### 2. 接口是统称

| 通信方式 | 接口类型 | 文件后缀 |
|---|---|---|
| 话题 | 消息接口 | `.msg` |
| 服务 | 服务接口 | `.srv` |
| 动作 | 动作接口 | `.action` |

它们都是 ROS2 接口，只是用途和文件后缀不同。

### 3. 接口包

接口功能包和普通功能包本质都是 ROS2 功能包，但接口包有特殊要求：

- 必须是 `ament_cmake` 类型。
- 必须依赖 `rosidl_default_generators`。
- 必须在 `package.xml` 中加 `<member_of_group>rosidl_interface_packages</member_of_group>`。
- 用 `rosidl_generate_interfaces` 生成接口代码。

接口包通常只放 `.msg`、`.srv`、`.action` 文件，不写节点业务逻辑。

---

## 九、接口设计思路

### 1. 先设计节点，再设计接口

- 系统里有哪些角色？
- 每个角色负责什么？
- 谁发数据？谁收数据？谁请求服务？

### 2. 按通信方式分类

- 持续流式数据 → 话题 `.msg`
- 一次请求一次响应 → 服务 `.srv`
- 长任务、有反馈、可取消 → 动作 `.action`

### 3. 每个通信需求一个接口文件

- 一个话题对应一个 `.msg`。
- 一个服务对应一个 `.srv`。
- 一个动作对应一个 `.action`。

不是“所有话题接口写成一个文件”，而是“每个接口一个文件”。

### 4. 功能复杂时接口会很多

功能越复杂，接口越多。  
按类型放在 `msg`、`srv`、`action` 文件夹里。

拆分信号：

- 不同话题传的数据不一样，就分开。
- 不同服务做的事不一样，就分开。
- 一个接口字段太多、太杂，考虑拆。

合并信号：

- 几个字段总是一起出现，可以放一个接口。

---

## 十、接口CLI命令

```bash
ros2 interface list                    # 列出所有接口
ros2 interface show <接口名>           # 查看接口详细定义
ros2 interface package <包名>          # 查看某个包下所有接口
ros2 interface packages                # 列出所有接口包
```

示例：

```bash
ros2 interface show std_msgs/msg/String
ros2 interface show example_interfaces/srv/AddTwoInts
ros2 interface package sensor_msgs
```

