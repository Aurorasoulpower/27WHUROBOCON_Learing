---
created: 2026-10-02
type: Note
tags:
  - "#ros2"
---

## 命令行接口

所有 ROS 2 CLI 工具都以 `ros2` 前缀开头，后面跟一个命令、一个动词以及可能的位置/可选参数。

查看某个工具的文档：

```bash
ros2 <command> --help
```

查看某个动词的文档：

```bash
ros2 <command> <verb> -h
```

自动补全适用于所有命令/动词以及大多数位置/可选参数，例如：

```bash
ros2 <command> [tab][tab]
```

下面一些示例依赖于：  
[ROS 2 demos 软件包](https://github.com/ros2/demos)

---

### `action`

允许手动发送目标，并显示有关动作的调试信息。

| 动词 | 说明 |
| --- | --- |
| `info` | 输出动作信息。 |
| `list` | 输出动作名称列表。 |
| `send_goal` | 发送动作目标。 |
| `show` | 输出动作定义。 |

示例：

```bash
ros2 action info /fibonacci
ros2 action list
ros2 action send_goal /fibonacci action_tutorials/action/Fibonacci "{order: 5}"
ros2 action show action_tutorials/action/Fibonacci
```

---

### `bag`

允许将话题记录到 rosbag 或从 rosbag 播放。

| 动词 | 说明 |
| --- | --- |
| `info` | 输出 bag 信息。 |
| `play` | 播放 bag。 |
| `record` | 记录 bag。 |

示例：

```bash
ros2 bag info <bag-name>
ros2 bag play <bag-name>
ros2 bag record -a
```

---

### `component`

与组件相关的各种动词。

| 动词 | 说明 |
| --- | --- |
| `list` | 输出正在运行的容器和组件列表。 |
| `load` | 将组件加载到容器节点中。 |
| `standalone` | 将组件运行到其独立的容器节点中。 |
| `types` | 输出在 ament 索引中注册的组件列表。 |
| `unload` | 从容器节点卸载组件。 |

示例：

```bash
ros2 component list
ros2 component load /ComponentManager composition composition::Talker
ros2 component types
ros2 component unload /ComponentManager 1
```

---

### `daemon`

与守护进程相关的各种动词。

| 动词 | 说明 |
| --- | --- |
| `start` | 如果守护进程未运行则启动它。 |
| `status` | 输出守护进程状态。 |
| `stop` | 如果守护进程正在运行则停止它。 |

---

### `doctor`

用于检查 ROS 设置以及其他潜在问题（如网络、软件包版本、rmw 中间件等）的工具。  
别名：`wtf`（where's the fire，哪里着火了）。

参数：

| 参数 | 说明 |
| --- | --- |
| `--report/-r` | 输出所有检查的报告。 |
| `--report-fail/-rf` | 仅输出失败检查的报告。 |
| `--include-warning/-iw` | 将警告包含为失败检查。 |

示例：

```bash
ros2 doctor
ros2 doctor --report
ros2 doctor --report-fail
ros2 doctor --include-warning
ros2 doctor --include-warning --report-fail
```

或者类似地：

```bash
ros2 wtf
```

---

### `extension_points`

列出扩展点。

---

### `extensions`

列出扩展。

---

### `interface`

与 ROS 接口（动作/话题/服务）相关的各种动词。  
接口类型可以通过以下任一选项过滤：`--only-actions`、`--only-msgs`、`--only-srvs`。

| 动词 | 说明 |
| --- | --- |
| `list` | 列出所有可用接口类型。 |
| `package` | 输出一个软件包内可用接口类型的列表。 |
| `packages` | 输出提供接口的软件包列表。 |
| `proto` | 打印接口的原型（主体）。 |
| `show` | 输出接口定义。 |

示例：

```bash
ros2 interface list
ros2 interface package std_msgs
ros2 interface packages --only-msgs
ros2 interface proto example_interfaces/srv/AddTwoInts
ros2 interface show geometry_msgs/msg/Pose
```

---

### `launch`

允许运行任意软件包中的 launch 文件，而无需先 `cd` 到那里。

用法：

```bash
ros2 launch <package> <launch-file>
```

示例：

```bash
ros2 launch demo_nodes_cpp add_two_ints.launch.py
```

---

### `lifecycle`

生命周期相关的各种动词。

| 动词 | 说明 |
| --- | --- |
| `get` | 获取一个或多个节点的生命周期状态。 |
| `list` | 输出可用转换列表。 |
| `nodes` | 输出具有生命周期的节点列表。 |
| `set` | 触发生命周期状态转换。 |

---

### `msg`

**（已弃用）** 显示有关消息的调试信息。

| 动词 | 说明 |
| --- | --- |
| `list` | 输出消息类型列表。 |
| `package` | 输出给定软件包内的消息类型列表。 |
| `packages` | 输出包含消息的软件包列表。 |
| `show` | 输出消息定义。 |

示例：

```bash
ros2 msg list
ros2 msg package std_msgs
ros2 msg packages
ros2 msg show geometry_msgs/msg/Pose
```

---

### `multicast`

多播相关的各种动词。

| 动词 | 说明 |
| --- | --- |
| `receive` | 接收单个 UDP 多播数据包。 |
| `send` | 发送单个 UDP 多播数据包。 |

---

### `node`

显示有关节点的调试信息。

| 动词 | 说明 |
| --- | --- |
| `info` | 输出节点信息。 |
| `list` | 输出可用节点列表。 |

示例：

```bash
ros2 node info /talker
ros2 node list
```

---

### `param`

允许操作参数。

| 动词 | 说明 |
| --- | --- |
| `delete` | 删除参数。 |
| `describe` | 显示已声明参数的描述信息。 |
| `dump` | 以 yaml 格式将给定节点的参数转储到终端或文件。 |
| `get` | 获取参数。 |
| `list` | 输出可用参数列表。 |
| `set` | 设置参数。 |

示例：

```bash
ros2 param delete /talker /use_sim_time
ros2 param get /talker /use_sim_time
ros2 param list
ros2 param set /talker /use_sim_time false
```

---

### `pkg`

创建 ros2 软件包或输出软件包相关信息。

| 动词 | 说明 |
| --- | --- |
| `create` | 创建新的 ROS2 软件包。 |
| `executables` | 输出软件包特定可执行文件列表。 |
| `list` | 输出可用软件包列表。 |
| `prefix` | 输出软件包的前缀路径。 |
| `xml` | 输出软件包 xml 清单中包含的信息。 |

示例：

```bash
ros2 pkg executables demo_nodes_cpp
ros2 pkg list
ros2 pkg prefix std_msgs
ros2 pkg xml -t version
```

---

### `run`

允许运行任意软件包中的可执行文件，而无需先 `cd` 到那里。

用法：

```bash
ros2 run <package> <executable>
```

示例：

```bash
ros2 run demo_nodes_cpp talker
```

---

### `security`

安全相关的各种动词。

| 动词 | 说明 |
| --- | --- |
| `create_key` | 创建密钥。 |
| `create_permission` | 创建权限。 |
| `generate_artifacts` | 生成密钥和权限文件。 |
| `list_keys` | 列出密钥。 |
| `create_keystore` | 创建密钥库。 |
| `distribute_key` | 分发密钥。 |
| `generate_policy` | 根据 ROS 图数据生成 XML 策略文件。 |

示例（参见 [sros2 软件包](https://github.com/ros2/sros2)）：

```bash
ros2 security create_key demo_keys /talker
ros2 security create_permission demo_keys /talker policies/sample_policy.xml
ros2 security generate_artifacts
ros2 security create_keystore demo_keys
```

---

### `service`

允许手动调用服务并显示有关服务的调试信息。

| 动词 | 说明 |
| --- | --- |
| `call` | 调用服务。 |
| `find` | 输出给定类型的服务列表。 |
| `list` | 输出服务名称列表。 |
| `type` | 输出服务类型。 |

示例：

```bash
ros2 service call /add_two_ints example_interfaces/AddTwoInts "{a: 1, b: 2}"
ros2 service find rcl_interfaces/srv/ListParameters
ros2 service list
ros2 service type /talker/describe_parameters
```

---

### `srv`

**（已弃用）** 与 srv 相关的各种动词。

| 动词 | 说明 |
| --- | --- |
| `list` | 输出可用服务类型列表。 |
| `package` | 输出一个软件包内可用服务类型列表。 |
| `packages` | 输出包含服务的软件包列表。 |
| `show` | 输出服务定义。 |

---

### `test`

运行 ROS2 launch 测试。

---

### `topic`

用于显示有关 ROS 话题的调试信息，包括发布者、订阅者、发布频率和消息。

| 动词 | 说明 |
| --- | --- |
| `bw` | 显示话题使用的带宽。 |
| `delay` | 显示话题相对于 header 中时间戳的延迟。 |
| `echo` | 将给定话题的消息输出到屏幕。 |
| `find` | 查找给定类型的话题。 |
| `hz` | 显示话题的发布频率。 |
| `info` | 输出给定话题的信息。 |
| `list` | 输出活动话题列表。 |
| `pub` | 向话题发布数据。 |
| `type` | 输出话题类型。 |

示例：

```bash
ros2 topic bw /chatter
ros2 topic echo /chatter
ros2 topic find rcl_interfaces/msg/Log
ros2 topic hz /chatter
ros2 topic info /chatter
ros2 topic list
ros2 topic pub /chatter std_msgs/msg/String 'data: Hello ROS 2 world'
ros2 topic type /rosout
```