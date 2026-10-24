---
created: 2026-10-02
type: Note
tags:
  - "#ros2"
  - "#网络通信"
---

## 一、通信底层基础

### 1.1 通信到底在解决什么问题

两个程序之间要传数据，不管是同一台机器上的两个进程，还是两台机器上的两个程序，都需要解决三个问题：

- 数据用什么格式表示
- 数据怎么从 A 传到 B
- 传丢了、传错了怎么办

这三个问题由通信协议来约定。协议规定了数据格式、传输方式、纠错规则。而协议最终要落到具体的通信方式上，也就是数据走什么物理通道。

### 1.2 三种通信方式

**UDP**

UDP 是无连接协议。发送方直接把数据包扔出去，不关心对方在不在、收没收到。它不保证送达，丢了就丢了，不会重传。

优点：快、延迟低、支持广播和多播。
缺点：不可靠，网络不好时可能丢数据。

适用场景：实时性要求高、允许少量丢包、需要广播。比如视频直播、传感器数据、DNS 查询。

**TCP**

TCP 是面向连接的协议。通信前先建立连接（三次握手），数据保证送达，丢了会重传，顺序也会保证。

优点：可靠，数据不丢、不乱序。
缺点：延迟比 UDP 高，因为要建立连接、确认、重传。

适用场景：数据不能丢、对实时性要求没那么极端的场景。比如文件传输、网页浏览、SSH。

**共享内存（SHM）**

共享内存是同一台机器上进程间通信的方式。两个进程映射同一块物理内存，一个写进去，另一个直接读出来。数据不需要经过网络协议栈，不需要序列化和反序列化。

优点：极快、延迟极低。
缺点：只能本机用，跨机器不行。

适用场景：同一台机器上的高频进程间通信。比如 ROS2 中同机的发布者和订阅者。

### 1.3 Linux 下验证三种通信方式

**UDP 验证**

```bash
ping 192.168.0.1
```

ping 发的是 ICMP Echo 请求，底层走 IP 协议，类似 UDP 的无连接思路：发出去等回复，不等回复就直接报超时。没有“建立连接”这一步。

**TCP 验证**

```bash
# 终端 A：监听 1234 端口
nc -l 1234

# 终端 B：连接并发送数据
echo "Hello, TCP!" | nc 127.0.0.1 1234
```

必须先监听、再连接，然后才能传数据。这个“先建立连接”的过程就是 TCP 面向连接的体现。

**共享内存验证**

```bash
ipcs -m                # 查看系统里已有的共享内存段
ipcrm -m <shmid>       # 删除指定的共享内存段
```

`ipcs -m` 会列出共享内存段的 ID、大小、创建进程等信息。如果 ROS2 异常退出，可能残留共享内存段，需要用 `ipcrm` 清理。

### 1.4 这三种方式在 ROS2 里的角色

ROS2 底层的 DDS 会根据数据大小、可靠性要求、网络环境，自动选择用 UDP、TCP 还是共享内存。你不需要手写 socket，但需要知道它们的存在，排错时有用。

- 本机通信：优先走共享内存
- 跨机通信：走 UDP
- 特殊场景（防火墙只允许 TCP、网络极不可靠）：可以配置走 TCP


## 二、DDS 与 FastDDS

### 2.1 ROS2 和 DDS 的分工

ROS2 本身不负责通信。它定义的是“节点怎么组织、话题怎么命名、服务怎么调用”这些上层规则。真正把数据从 A 节点搬到 B 节点的，是 DDS。

ROS2 和 DDS 之间有一层抽象接口，叫 RMW（ROS Middleware Interface）。ROS2 的上层代码只跟 RMW 打交道，不直接跟 DDS 打交道。RMW 下面接的可以是 FastDDS，也可以是 CycloneDDS，也可以是其他 DDS 实现。

分层结构：

```text
你写代码
    ↓
调用 rclpy / rclcpp API
    ↓
ROS2 RMW 层
    ↓
DDS 中间件（默认 Fast DDS）
    ↓
UDP / 共享内存 / TCP
```

所以你做应用开发时，接触到的永远是 ROS2 这一层，不是 DDS 那一层。DDS 在底下默默干活。

### 2.2 RTPS 协议

DDS 标准定义了一套通信协议，叫 RTPS（Real-Time Publish-Subscribe）。所有 DDS 实现都必须支持这个协议，否则不同厂家的 DDS 就没法互通。

RTPS 的核心模型就是发布/订阅：

- 一个参与者（Participant）可以创建多个发布者（Writer）和订阅者（Reader）
- 发布者往某个 Topic 写数据
- 订阅者从同一个 Topic 读数据
- 双方通过“发现”机制找到彼此

这个模型和你学的 ROS2 话题通信在概念上完全一样。区别只是名字不同：

| ROS2 | RTPS |
|------|------|
| Node | Participant |
| Publisher | DataWriter |
| Subscription | DataReader |
| Topic | Topic |

ROS2 的 `create_publisher` 底层就是在创建一个 RTPS 的 DataWriter，`create_subscription` 底层就是在创建一个 RTPS 的 DataReader。QoS 配置也是从 ROS2 的 QoS 映射到 RTPS 的 QoS。

### 2.3 FastDDS 是什么

FastDDS 是 eProsima 公司开发的一个 DDS 实现，用 C++ 写的，开源。它是大多数 ROS2 发行版的默认通信中间件。

对应的 RMW 实现叫 `rmw_fastrtps_cpp`。

FastDDS 在 ROS2 里的角色：

- 你调用 `create_publisher`，ROS2 通过 RMW 翻译成 FastDDS 的 `create_datawriter`
- 你调用 `create_subscription`，ROS2 翻译成 FastDDS 的 `create_datareader`
- 你配置 QoS，ROS2 翻译成 FastDDS 的 QoS 策略
- FastDDS 用 RTPS 协议做发现和数据传输
- 传输时根据情况选 UDP、SHM 或 TCP

### 2.4 三种传输方式在 FastDDS 里的选择逻辑

当你运行一个 ROS2 系统时，FastDDS 的选择顺序是：

1. **节点发现**：始终用 UDP（或 TCP，如果配置了）。因为发现需要广播和多播，UDP 天然支持。
2. **同机数据传输**：优先用 SHM。两个进程在同一台机器上时，FastDDS 自动切换到共享内存，速度极快。
3. **跨机数据传输**：用 UDP。
4. **如果显式配置了 TCP**，且 UDP 不适用，才用 TCP。

这个选择是自动的，你不需要手动干预。除非你有特殊需求，比如禁用 SHM、强制用 TCP，那才需要通过 XML 配置文件来改。

### 2.5 节点发现机制

当一个 ROS2 节点启动时，它会做几件事：

1. 创建一个 DDS Participant
2. 向网络广播“我存在，我的 IP 是 xxx，我监听端口 yyy”
3. 同时监听其他节点的广播
4. 发现其他节点后，交换各自发布了哪些话题、订阅了哪些话题、QoS 是什么

这个过程叫“发现”。发现完成后，发布者和订阅者才知道彼此的存在，才能建立数据通道。

发现依赖多播。多播在局域网里通常没问题，但在以下场景会失败：

- 两台机器在不同的子网，路由器不转发多播
- 防火墙阻止了多播包
- 虚拟机或 Docker 的网络配置不支持多播
- WiFi 网络对多播支持不好

发现失败的表现是：两台机器上的节点互相看不到，`ros2 node list` 只显示本机的节点，`ros2 topic list` 看不到对方的话题。

### 2.6 RMW 实现可以切换

ROS2 不绑定某一个 DDS 实现。你可以切换 RMW，让 ROS2 用不同的 DDS 来通信。

常见 RMW 实现：

- `rmw_fastrtps_cpp`：对应 FastDDS，大多数 ROS2 发行版的默认选择
- `rmw_cyclonedds_cpp`：对应 CycloneDDS，Eclipse 基金会开发
- `rmw_connextdds`：对应 RTI Connext，商业 DDS

切换方式：

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

然后重新启动节点。所有节点必须用同一个 RMW 实现，否则互相发现不了。

不同 RMW 实现的特点：

- FastDDS：默认选择，功能全，配置灵活
- CycloneDDS：轻量，在某些场景下延迟更低
- Connext：商业产品，有技术支持，适合工业场景

大多数情况下，用默认的 FastDDS 就行。

### 2.7 QoS 在底层的映射

你之前学的 QoS 配置项，到了 DDS 这一层，会映射成 RTPS 的 QoS 策略。

- ROS2 的 `ReliabilityPolicy.RELIABLE` → RTPS 的 `RELIABLE`
- ROS2 的 `ReliabilityPolicy.BEST_EFFORT` → RTPS 的 `BEST_EFFORT`
- ROS2 的 `DurabilityPolicy.TRANSIENT_LOCAL` → RTPS 的 `TRANSIENT_LOCAL`
- ROS2 的 `DurabilityPolicy.VOLATILE` → RTPS 的 `VOLATILE`

映射关系是一一对应的。不兼容的判定也是在 DDS 层做的：发布器的 DataWriter 和订阅器的 DataReader 的 QoS 策略如果不兼容，DDS 就不会建立数据通道，订阅器就收不到数据。

这也解释了为什么 QoS 不兼容时，错误信息里会出现 `RMW_QOS_POLICY_RELIABILITY` 这样的字样——它是从 RMW 层报上来的。


## 三、ROS2 的通信封装

### 3.1 ROS2 默认帮你做了什么

ROS2 默认内置 DDS，通信底层基本不用自己管。创建发布者、订阅者、服务，底层发现、连接、序列化、传输、重连，DDS 全包。

同一台机器上，DDS 自动用共享内存加速。跨机器时，DDS 自动用 UDP 发现和传输。你不需要写一行 socket 代码，不需要配网络参数，不需要管序列化格式。

这就是 ROS2 相比直接写 DDS 或 ZeroMQ 的最大优势：省心。

### 3.2 仍然需要了解的点

虽然底层不用管，但以下几个点出问题时需要知道往哪查：

| 项目 | 何时关注 | 说明 |
|------|----------|------|
| QoS | 消息丢失、订阅不到 | 可靠性、历史、深度等策略，不匹配会通信失败 |
| Domain ID | 多机 / 实验室环境 | 不同 ID 互相看不见，改 `ROS_DOMAIN_ID` 隔离 |
| RMW 实现 | 性能调优、特殊平台 | 默认 Fast DDS，可换 CycloneDDS 等 |
| 网络环境 | 节点发现不了 | 多播被禁时需配置单播发现 |
| 共享内存 | 同机通信异常 | 残留时用 `ipcs -m` / `ipcrm` 清理 |

### 3.3 什么时候需要自己管通信

大多数 ROS2 应用开发不需要自己管通信。以下场景才需要往下走：

- 不用 ROS2，直接拿 DDS 或 ZeroMQ 写程序
- 极端性能优化：自定义序列化、零拷贝、实时调度
- 非标准网络，多播完全不可用，需手写 DDS 配置
- 把 ROS2 和 non-ROS 系统集成，需要桥接


## 四、Domain ID 与端口

### 4.1 Domain ID 是什么

ROS2 的节点通过 DDS 通信。DDS 把网络划分成不同的“域”（Domain），每个域是一个逻辑上的独立网络。

Domain ID 就是这个域的编号。不同 Domain ID 的节点互相看不到，即使它们在同一台机器上、同一个网段里。

这类似 VLAN 的概念：物理上在同一张网，逻辑上被隔离开。

底层关系：

```text
Domain ID 不同 → 计算出的 UDP 端口段不同 → 互相收不到消息
Domain ID 相同 → 端口段一致 → 可以互相发现并通信
```

### 4.2 端口计算

DDS 默认占用 7400-8000 附近的端口。计算公式（了解即可，不用手算）：

```text
端口 = 7400 + 250 * DomainID + ...
每个 Domain 占 250 个端口
最大 Domain ID = 232（再大就超过 65535）
```

默认 Domain ID 是 0。推荐使用 1-101 之间的值。

### 4.3 设置 Domain ID

```bash
# 临时设置（只对当前终端有效）
export ROS_DOMAIN_ID=1

# 永久设置（推荐）
echo "export ROS_DOMAIN_ID=1" >> ~/.bashrc
source ~/.bashrc

# 验证
echo $ROS_DOMAIN_ID
```

### 4.4 三大典型场景

**场景一：多机通信**

两台电脑互通：

```bash
# 电脑 A
export ROS_DOMAIN_ID=7
ros2 run demo_nodes_cpp talker

# 电脑 B
export ROS_DOMAIN_ID=7
ros2 run demo_nodes_cpp listener
```

规则：相同 Domain ID + 同一 WiFi/网段 = 可通信。

**场景二：实验室隔离**

避免多组人互相干扰：

```bash
# 第一组
export ROS_DOMAIN_ID=1

# 第二组
export ROS_DOMAIN_ID=2

# 第三组
export ROS_DOMAIN_ID=3
```

各自 `ros2 node list` 只能看到自己的节点，互不干扰。

**场景三：多机器人系统**

同一网络下，两个机器人的节点完全隔离：

```bash
# 机器人 A
export ROS_DOMAIN_ID=10

# 机器人 B
export ROS_DOMAIN_ID=20
```

### 4.5 常见坑与排错

| 问题 | 原因 | 解决 |
|------|------|------|
| `ros2 node list` 看不到对方 | Domain ID 不一致 | 检查双方 `echo $ROS_DOMAIN_ID` |
| 节点互相串台 | 都用默认 0 | 每人改不同 ID |
| 两台电脑无法通信 | 不在同一网段 / 防火墙 | 检查网络，开放 UDP 7400-8000 |
| 报错 `Address already in use` | Domain ID 太大或进程过多 | 换小 ID，减少节点数 |

排错命令：

```bash
echo $ROS_DOMAIN_ID       # 查看当前 Domain ID
ros2 node list            # 查看节点列表
ss -tulpn | grep 74       # 查看 DDS 端口占用
```

进程数量限制：同一台机器、同一个 Domain 下，最多约 120 个 ROS2 进程。超过后端口会溢出到下一个 Domain，可能造成冲突。普通开发远远用不到这个上限。


## 五、通信方案对比：FastDDS vs ZeroMQ

### 5.1 ZeroMQ 是什么

ZeroMQ 是一个轻量级消息中间件。它的特点是：

- 无 broker：不需要一个中心节点来转发消息
- 零代理：消息直接在发送方和接收方之间传递
- 零延迟：设计上追求低延迟
- 零管理：不需要复杂的配置和管理

它提供了进程内、进程间、TCP、多播的 socket 抽象。你可以把它理解成“更好用的 socket 库”。

### 5.2 ZeroMQ 的核心模式

| 模式 | 作用 |
|------|------|
| PUB/SUB | 发布-订阅，一个发多个收 |
| REQ/REP | 请求-应答，类似 RPC |
| PUSH/PULL | 任务分发，推端发，拉端收 |

### 5.3 PyZMQ 示例

发布端：

```python
import zmq
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")
while True:
    socket.send_string("topic1 Hello")
```

订阅端：

```python
import zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"topic1")
while True:
    print(socket.recv_string())
```

### 5.4 与 FastDDS 对比

| 维度 | FastDDS | ZeroMQ |
|------|---------|--------|
| 定位 | ROS2 标准中间件 | 轻量级通信库 |
| 发现机制 | 自动发现（DDS 协议） | 手动配置连接地址 |
| 依赖 | 较重，需完整 ROS2 环境 | 极轻，无外部依赖 |
| 适用场景 | 标准 ROS2 机器人系统 | 自研轻量系统、多进程高频通信 |
| 小数据延迟 | 更低 | 稍高 |
| 大数据吞吐 | 稍低 | 更高 |

### 5.5 选型建议

- 已在用 ROS2 → FastDDS
- 自研轻量系统、多进程高频通信、不想引入完整 ROS2 → ZeroMQ

ZeroMQ 的优势不在“比 DDS 快”，而在足够小、简单、灵活。它不需要 DDS 的发现机制，不需要 QoS 配置，不需要 ROS2 环境，拿来就能用。


## 六、实战速查

### 6.1 通信底层

```bash
ping 192.168.0.1          # UDP 演示
nc -l 1234                # TCP 监听
ipcs -m                   # 查看共享内存
ipcrm -m <shmid>          # 删除共享内存
```

### 6.2 ROS2 通信排查

```bash
echo $ROS_DOMAIN_ID       # 查看域 ID
ros2 node list            # 查看节点
ros2 topic list           # 查看话题
ros2 topic info /xxx --verbose   # 查看话题 QoS
ros2 doctor               # 系统诊断
ss -tulpn | grep 74       # 查看 DDS 端口占用
```

### 6.3 必会与了解

**必须会：**

- 节点、话题、服务、动作、参数
- `ros2 run / node / topic / service / param`
- QoS 基本概念
- `ROS_DOMAIN_ID` 设置
- 多机通信：同网段、同 Domain ID、防火墙、多播
- 常见排查：`ros2 doctor`、`topic echo`、`node info`

**了解即可：**

- DDS / RMW、Fast DDS、CycloneDDS
- Domain ID 与端口关系
- 共享内存、ZeroMQ


## 七、一张图串起所有内容

```text
你写 ROS2 代码
    ↓
调用 rclpy / rclcpp API
    ↓
ROS2 RMW 层（翻译）
    ↓
DDS 中间件（默认 FastDDS）
    ↓
RTPS 协议（发现 + 传输）
    ↓
┌─────────────┬─────────────┬─────────────┐
│   UDP       │    SHM      │    TCP      │
│ 跨机通信    │ 同机高速    │ 特殊场景    │
│ 发现+传输   │ 数据传输    │ 可靠传输    │
└─────────────┴─────────────┴─────────────┘
    ↓
Domain ID 决定端口段
    ↓
不同 Domain ID 逻辑隔离
```

核心结论：底层通信交给 DDS，你只管用 ROS2 API。需要关注的是 QoS、Domain ID、RMW 实现和网络环境，这四样出问题时知道往哪查就行。