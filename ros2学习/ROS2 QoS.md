---
created: 2026-10-04
type: Note
tags:
  - "#ros2"
  - "#节点通信"
---
## 〇、QoS速查

### 核心 QoS 参数速查

| 参数 | 作用 | 可选值 | 常用配置 | 备注 |
|------|------|--------|----------|------|
| History | 发布端缓存策略 | Keep last / Keep all | Keep last | 通常配合 Depth 使用 |
| Depth | 队列深度 | 整数 | 传感器 5~10；参数 1000；默认 10 | 仅 History=Keep last 时有效 |
| Reliability | 可靠性 | Best effort / Reliable | 传感器 Best effort；控制 Reliable | 最易导致不兼容 |
| Durability | 持久性 | Volatile / Transient local | 传感器 Volatile；地图 Transient local | 第二易导致不兼容 |
| Deadline | 最大发布间隔 | 时间 | 控制指令可设 | 默认无穷大 |
| Lifespan | 数据有效期 | 时间 | 传感器可设 | 默认无穷大 |
| Liveliness | 活跃性检测 | Automatic / Manual by topic | Automatic | 默认 Automatic |
| Lease Duration | 租约时长 | 时间 | 配合 Liveliness | 默认无穷大 |

### 常用 QoS 预设速查

| 预设名                          | 典型场景       | Python 导入                                            | History/Depth    | Reliability | Durability |
| ---------------------------- | ---------- | ---------------------------------------------------- | ---------------- | ----------- | ---------- |
| qos_profile_sensor_data      | 激光、摄像头、IMU | `from rclpy.qos import qos_profile_sensor_data`      | Keep last / 5    | Best effort | Volatile   |
| qos_profile_parameters       | 参数事件       | `from rclpy.qos import qos_profile_parameters`       | Keep last / 1000 | Reliable    | Volatile   |
| qos_profile_services_default | 服务通信       | `from rclpy.qos import qos_profile_services_default` | Keep last / 10   | Reliable    | Volatile   |
| qos_profile_system_default   | 一般话题默认     | `from rclpy.qos import qos_profile_system_default`   | Keep last / 10   | Reliable    | Volatile   |

### 常见场景 QoS 配置速查

| 场景 | Reliability | Durability | Depth | 代码要点 |
|------|-------------|------------|-------|----------|
| 订阅传感器 | Best effort | Volatile | 5~10 | 直接用 `qos_profile_sensor_data` |
| 发布地图 | Reliable | Transient local | 1 | `QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)` |
| 发布控制指令 | Reliable | Volatile | 1~10 | `QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)` |
| 订阅控制指令 | Best effort | Volatile | 1~10 | 兼容发布器的 Reliable，但可能丢数据 |
| 一般话题 | Reliable | Volatile | 10 | 默认即可 |

## 一、为什么 ROS2 需要 QoS

### 1.1 ROS1 通信的局限

ROS1 的节点通信底层基于 TCP。TCP 的特点是可靠传输：发出去的数据一定会送到，如果中间丢了，会自动重传，直到对方收到为止。

这个机制在大多数场景下没问题，但在以下场景会出问题。

**网络不稳定时**

机器人通过 WiFi 和远程主机通信，信号时好时坏。TCP 为了可靠，会不断重传丢失的数据。结果就是数据确实送到了，但延迟可能从几毫秒变成几百毫秒甚至几秒。对于控制指令来说，一个延迟 2 秒的“前进”命令，可能比“丢失”更危险。

**传感器数据量大时**

激光雷达每秒产生几十万的点，图像每秒几十兆的字节。这些数据如果用 TCP 可靠传输，一旦网络稍有波动，重传的数据会堆积，导致整个通信链路越来越慢。

**实时性要求高时**

有些场景下旧数据毫无价值。比如你订阅激光雷达数据做避障，如果当前这一刻的数据没收到，你更希望拿到下一秒的新数据，而不是等 TCP 把旧数据重传过来。因为等你收到旧数据时，机器人可能已经撞上去了。

### 1.2 ROS2 的解法：DDS 和 QoS

ROS2 把通信中间件换成了 DDS。DDS 最初是为实时系统设计的，它不强制用 TCP，可以用 UDP，也可以用共享内存。更重要的是，DDS 允许你针对每个发布器、每个订阅器单独配置通信质量。

这个“通信质量配置”就是 QoS（Quality of Service）。

QoS 的核心思想是：不同场景对通信的要求不同，不应该用一套固定的规则。

- 传感器数据：丢一两个没关系，但要快，用 Best Effort
- 控制指令：绝对不能丢，用 Reliable
- 地图数据：后加入的节点也需要之前的数据，用 Transient Local
- 实时数据：过期的数据直接丢，设置 Lifespan

### 1.3 QoS 不兼容的后果

QoS 是发布器和订阅器各自独立配置的。如果两边的配置冲突，通信就无法建立。

典型表现：

- 发布器端报错：`New subscription discovered on topic '/xxx', offering incompatible QoS`
- 订阅器端报错：`New publisher discovered on topic '/xxx', offering incompatible QoS. No messages will be received from it. Last incompatible policy: RELIABILITY`
- 结果：订阅器一个消息都收不到

最后那句 `Last incompatible policy: RELIABILITY` 是关键线索，它告诉你具体是哪一项 QoS 策略不兼容。


## 二、QoS 的八个配置项

QoS 一共有八个可配置的策略。不是每个都必须配，不配的会用默认值。

### 2.1 History（历史记录策略）

**作用**

决定发布器如何保存待发送的数据。

**两个选项**

`Keep last`：只保留最新的 N 条数据。N 由 Depth 决定。当队列满了，新的数据会挤掉旧的数据。

`Keep all`：保留所有数据。但实际上受限于 DDS 底层的资源限制，不可能真的无限保留。

**实际含义**

假设你设置 `Keep last, Depth=10`。发布器快速发了 100 条消息，但订阅器处理得慢，只消费了 80 条。那么发布器队列里始终只有最新的 10 条，最早的那些已经被挤掉了。

**什么时候用哪个**

绝大多数场景用 `Keep last`，因为你通常只关心最新的数据。`Keep all` 很少用，除非你有特殊需求，比如要记录所有历史数据。

### 2.2 Depth（队列深度）

**作用**

当 `History = Keep last` 时，Depth 决定队列里保留多少条数据。

**实际含义**

Depth 太小，订阅器处理慢的时候会丢数据。Depth 太大，会占更多内存。

**常用值**

- 传感器数据：5 到 10 就够了，反正只关心最新的
- 控制指令：1 到 10，通常只关心最新的一条
- 参数事件：1000，因为参数变化需要都收到

### 2.3 Reliability（可靠性策略）

**作用**

决定数据传送的可靠程度。

**两个选项**

`Best effort`：尽力传送。网络好的时候能收到，网络不好时可能丢数据，不重传。

`Reliable`：确保送达。如果丢了会重传，直到对方确认为止。可能因为重传导致延迟增大。

**实际含义**

这是最容易导致 QoS 不兼容的一项。

传感器数据通常用 `Best effort`，因为数据量大、重传代价高、丢一两帧没关系、实时性比完整性重要。

控制指令、服务请求通常用 `Reliable`，因为数据量小、重传代价低、丢了可能导致机器人行为异常、完整性比实时性重要。

**兼容规则**

| 发布器 | 订阅器 | 是否兼容 |
|--------|--------|----------|
| Reliable | Reliable | 兼容 |
| Reliable | Best effort | 兼容 |
| Best effort | Reliable | 不兼容 |
| Best effort | Best effort | 兼容 |

记忆方法：发布器的可靠性可以“降级”满足订阅器。发布器是 Reliable，订阅器只要 Best effort，那没问题。但发布器是 Best effort，订阅器要求 Reliable，发布器做不到，所以不兼容。

### 2.4 Durability（持久性策略）

**作用**

决定发布器是否为“后加入的订阅者”保留数据。

**两个选项**

`Volatile`：不保留。订阅者加入之前发布的数据，订阅者收不到。

`Transient local`：保留。发布器会为后加入的订阅者保留数据，订阅者一加入就能收到最近的数据。

**实际含义**

这个策略解决的是“晚来的订阅者能不能拿到之前的数据”的问题。

典型场景：地图发布器。地图数据是静态的，发布一次就不变了。但如果订阅者在发布之后才启动，用 `Volatile` 的话，订阅者永远收不到地图。用 `Transient local`，发布器会保留最后一份地图，新订阅者一加入就发给他。

**兼容规则**

| 发布器 | 订阅器 | 是否兼容 |
|--------|--------|----------|
| Transient local | Transient local | 兼容 |
| Transient local | Volatile | 兼容 |
| Volatile | Transient local | 不兼容 |
| Volatile | Volatile | 兼容 |

记忆方法：发布器能提供“持久化”服务，订阅器可以不要。但发布器不提供，订阅器却要求，就不行。

### 2.5 Deadline（截止时间）

**作用**

设置数据发布的最大间隔时间。如果超过这个时间没有新数据，就认为发布器“违约”了。

**实际含义**

比如你设置 Deadline 为 100ms。正常情况下发布器每 50ms 发一次数据。如果某段时间发布器卡住了，超过 100ms 没发数据，订阅器会收到一个 Deadline 事件，知道数据断流了。

**什么时候用**

- 控制指令：希望固定间隔下发，超时说明控制链路有问题
- 心跳检测：定期检查某个节点是否还在正常工作

**默认值**

无穷大，即没有 Deadline 限制。

### 2.6 Lifespan（数据有效期）

**作用**

设置一条数据从发布到被接收的最大有效时间。超过这个时间的数据，即使收到了也会被丢弃。

**实际含义**

比如你设置 Lifespan 为 200ms。发布器在 t=0 发了一条数据，但由于网络延迟，订阅器在 t=300ms 才收到。因为超过了 200ms 的有效期，这条数据会被直接丢弃，不会交给回调函数。

**什么时候用**

- 传感器数据：过期的传感器数据毫无价值，不如丢掉
- 实时控制：旧的控制指令可能已经不安全了
- 仿真环境：通常不设置，因为仿真时间可能和真实时间不一致

**默认值**

无穷大，即数据永远有效。

### 2.7 Liveliness（活跃性策略）

**作用**

决定如何判断一个发布器是否还“活着”。

**两个选项**

`Automatic`：自动判断。一个节点可能有多个发布器，只要其中任意一个发布了数据，系统就认为该节点的所有发布器在接下来的 Lease Duration 内是活跃的。

`Manual by topic`：手动确认。发布器需要主动声明“我还活着”，系统才认为它活跃。

**实际含义**

这个策略主要用于检测节点是否崩溃或断连。如果发布器超过 Lease Duration 没有表现活跃，订阅器会收到一个 Liveliness 事件，知道发布器可能出问题了。

**什么时候用**

大多数场景用 `Automatic` 就够了。`Manual by topic` 用在需要精确控制活跃性声明的场景。

### 2.8 Lease Duration（租约时长）

**作用**

与 Liveliness 配合使用。规定发布器在这段时间内必须表现活跃，否则被认为停止工作。

**实际含义**

比如设置 Lease Duration 为 2 秒，Liveliness 为 Automatic。如果发布器超过 2 秒没有发布任何数据，订阅器就会认为这个发布器已经“失活”了。

**默认值**

无穷大，即不检测失活。


## 三、系统预设的 QoS 组合

每次手动配八个策略太麻烦。ROS2 提供了一些预设组合，直接拿来用就行。

### 3.1 Sensor Data QoS

适用于传感器数据。

```
History: Keep last
Depth: 5
Reliability: Best effort
Durability: Volatile
Deadline: Default
Lifespan: Default
Liveliness: System default
```

典型特征是 `Best effort + Volatile`。适合激光雷达、摄像头、IMU 等高频传感器。

### 3.2 Parameters QoS

适用于参数事件。

```
History: Keep last
Depth: 1000
Reliability: Reliable
Durability: Volatile
Deadline: Default
Lifespan: Default
Liveliness: System default
```

Depth 很大，因为参数变化事件不能丢。Reliability 是 Reliable，因为参数变化必须可靠传达。

### 3.3 其他预设

ROS2 还提供了 `qos_profile_system_default`、`qos_profile_services_default` 等预设。具体可以查看 `/opt/ros/<distro>/include/rmw/qos_profiles.h`。


## 四、Python 中配置 QoS

### 4.1 用预设

```python
from rclpy.qos import qos_profile_sensor_data

self.subscription = self.create_subscription(
    LaserScan,
    '/scan',
    self.scan_callback,
    qos_profile_sensor_data
)
```

### 4.2 手动配置

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE
)

self.publisher = self.create_publisher(String, '/my_topic', qos)
```

### 4.3 API 名称的版本差异

不同 ROS2 版本，QoS 相关的枚举类名可能不同：

- Foxy 及之前：`QoSReliabilityPolicy`、`QoSDurabilityPolicy`
- Galactic 及之后：`ReliabilityPolicy`、`DurabilityPolicy`

写代码时先确认 ROS2 版本，或者查看 `rclpy.qos` 模块里有哪些名字。


## 五、QoS 不兼容排查

### 5.1 查看话题的 QoS 信息

```bash
ros2 topic info /scan --verbose
```

输出示例：

```
Type: sensor_msgs/msg/LaserScan

Publisher count: 1

Node name: laserscan
Node namespace: /
Topic type: sensor_msgs/msg/LaserScan
Endpoint type: PUBLISHER
GID: 71.03.10.01...
QoS profile:
  Reliability: BEST_EFFORT
  Durability: VOLATILE
  Lifespan: 9223372036854775807 nanoseconds
  Deadline: 9223372036854775807 nanoseconds
  Liveliness: AUTOMATIC
  Liveliness lease duration: 9223372036854775807 nanoseconds

Subscription count: 0
```

这里能看到发布器的完整 QoS 配置。`Subscription count: 0` 说明当前没有订阅者。

### 5.2 对比发布器和订阅器的 QoS

如果自己写的订阅器收不到消息，用上面的命令看发布器的 QoS，然后看订阅器代码里的 QoS，逐项对比。

重点检查：

1. Reliability：发布器是 Best effort，订阅器是 Reliable，不兼容
2. Durability：发布器是 Volatile，订阅器是 Transient local，不兼容

### 5.3 看错误信息里的 Last incompatible policy

订阅器端的警告会明确告诉你哪一项不兼容：

```
[WARN] [subscriber_qos_obj]: New publisher discovered on topic '/qos_test', 
offering incompatible QoS. No messages will be received from it. 
Last incompatible policy: RELIABILITY
```

`Last incompatible policy: RELIABILITY` 说明是可靠性策略不兼容。

### 5.4 修改配置

知道哪一项不兼容后，修改订阅器的 QoS 去适配发布器。

比如发布器是 `Best effort`，订阅器就要改成 `Best effort`，不能要求 `Reliable`。

### 5.5 常见不兼容场景

| 场景 | 发布器 | 订阅器 | 结果 |
|------|--------|--------|------|
| 订阅传感器 | Best effort | Reliable | 不兼容 |
| 订阅地图 | Volatile | Transient local | 不兼容 |
| 订阅控制 | Reliable | Best effort | 兼容但订阅器可能丢数据 |
| 订阅传感器 | Best effort | Best effort | 兼容 |


## 六、发布器不兼容事件回调

### 6.1 它解决什么问题

发布器可以注册一个回调，当发现有订阅器 QoS 不兼容时触发。它做且只做一件事：告诉你“刚才有个订阅者因为 QoS 不兼容，连不上我”。

它不会自动修改 QoS 去适配订阅者，不会阻止不兼容的订阅者连接，不会让通信恢复正常，不会重试或降级。它就是一个通知。

### 6.2 它是可观测性工具，不是健壮性工具

健壮性指的是系统在异常情况下仍能正常工作，比如网络断了自动重连、数据丢了自动重传。

可观测性指的是系统出问题时，你能多快知道、多快定位。

这个回调属于后者。它不修复问题，但它让你在问题发生的第一时间就知道。

准确的说法是：在代码里放一段不兼容 QoS 事件回调，可以大大增强可观测性和可诊断性，降低排查难度。但它本身不增强健壮性。

### 6.3 代码示例

```python
from rclpy.qos_event import PublisherEventCallbacks

event_callbacks = PublisherEventCallbacks(
    incompatible_qos=self.incompatible_qos_clb
)

self.publisher = self.create_publisher(
    String,
    '/qos_test',
    qos_profile,
    event_callbacks=event_callbacks
)

def incompatible_qos_clb(self, event):
    self.get_logger().error("有订阅器 QoS 不兼容！")
    self.get_logger().error(str(event.last_policy_kind))
```

### 6.4 版本差异

`rclpy.qos_event` 这个模块在 Foxy 里存在，API 是 `PublisherEventCallbacks`。但到了 Galactic、Humble，rclpy 的 QoS 事件 API 变动过，有些版本里 `PublisherEventCallbacks` 的导入路径、参数名、事件对象的属性名都可能不一样。

用之前先确认版本：

```bash
python3 -c "import rclpy.qos_event; print(dir(rclpy.qos_event))"
```

如果这个版本没有，可以考虑用 C++ 写这个发布器，rclcpp 的 QoS 事件 API 相对稳定。

### 6.5 使用注意

**只在“发现订阅者”时触发**

DDS 的发现机制是：发布器启动后，周期性广播自己的存在。订阅者启动后，也广播。双方互相发现后，交换 QoS 信息。如果不兼容，发布器触发一次事件。

如果订阅者断开又重连，可能会再次触发。所以回调里不要做重操作，也不要假设它只触发一次。

**日志可能刷屏**

如果网络不稳定，订阅者反复断连重连，这个回调会反复触发。生产环境里通常会在回调里加一个计数器或时间窗口，比如“同一种不兼容策略，10 秒内只打印一次”。

**它只覆盖发布器端**

订阅器端也有类似的机制。rclpy 里对应的是 `SubscriptionEventCallbacks`，同样有 `incompatible_qos` 事件。订阅器端触发时，rclpy 默认就会打印警告，不需要额外注册。发布器端默认不打印，才需要手动注册。

### 6.6 什么时候值得放

**值得放的情况**

- 你写的是给别人用的发布器，别人会订阅你的话题，你不知道他们的 QoS 怎么配
- 你在调试阶段，任何能加速排查的手段都值得用
- 你的发布器是关键链路，比如控制指令发布器

**不值得放的情况**

- 你写的是内部临时节点，两端 QoS 都是你控制的
- 高频发布的传感器节点，日志刷屏风险高
- 你已经在用统一预设，QoS 不兼容的概率很低

### 6.7 折中方案

写一个辅助函数，只在需要时注册：

```python
def create_publisher_with_qos_check(node, msg_type, topic, qos_profile, enable_qos_event=False):
    if enable_qos_event:
        event_callbacks = PublisherEventCallbacks(
            incompatible_qos=lambda event: node.get_logger().error(
                f"QoS 不兼容：{event.last_policy_kind}"
            )
        )
        return node.create_publisher(
            msg_type, topic, qos_profile, event_callbacks=event_callbacks
        )
    else:
        return node.create_publisher(msg_type, topic, qos_profile)
```

调试时打开，生产时关掉。


## 七、实战建议

### 7.1 默认配置

如果不确定，用系统默认的 QoS。ROS2 的默认配置是：

- Reliability: Reliable
- Durability: Volatile
- History: Keep last, Depth: 10

大多数话题用默认配置都能正常工作。

### 7.2 什么时候需要改

**订阅传感器数据时**

传感器发布器通常用 `Best effort`。订阅器如果也用默认的 `Reliable`，就会不兼容。所以订阅激光雷达、摄像头等传感器时，要用：

```python
from rclpy.qos import qos_profile_sensor_data
```

**发布地图时**

地图是静态数据，后加入的节点也需要。要用：

```python
qos = QoSProfile(
    depth=1,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    reliability=ReliabilityPolicy.RELIABLE
)
```

**控制指令**

用 `Reliable` 确保送达。

### 7.3 RViz 显示不了数据

这通常就是 QoS 不兼容。RViz 的默认订阅 QoS 是 `Reliable`，而激光雷达发布器通常是 `Best effort`。所以 RViz 收不到激光数据。

解决方法：在 RViz 里找到对应话题的 QoS 设置，把 Reliability 改成 `Best effort`。
