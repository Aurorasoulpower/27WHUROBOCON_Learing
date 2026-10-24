---
created: 2026-10-05
type: Note
tags:
  - ros2
  - 节点通信
---
# ROS2 Action 通信

## 一、为什么需要 Action

### 1.1 三种已有通信方式的局限

前面学了话题、服务、参数，它们各自解决一类问题：

| 通信方式 | 模型 | 适用场景 |
|----------|------|----------|
| 话题 | 发布/订阅 | 单向、频繁、持续的数据流 |
| 服务 | 请求/响应 | 双向、一次性的短任务 |
| 参数 | 键值配置 | 节点设置值 |

但有一类场景它们都覆盖不好：**让机器人执行一个需要持续一段时间、过程中需要反馈、还可能中途取消的任务**。

### 1.2 用服务做长任务的三个问题

教材举的例子：通过服务发送一个目标点，让机器人移动到该点。

**问题一：不知道服务端有没有处理请求**

**问题二：执行过程中没有反馈**

**问题三：中途没法取消**

### 1.3 Action 的适用场景

这类场景在机器人里非常常见：导航、机械臂运动、小乌龟旋转，全都是“执行一段时间、过程中有进度、可以中途取消”的任务。

ROS2 针对这类场景，基于话题和服务，设计了 Action。

## 二、Action 的组成

### 2.1 三大组成

| 组成 | 含义 | 方向 | 解决什么问题 |
|------|------|------|-------------|
| 目标（Goal） | 客户端告诉服务端要做什么 | 客户端 → 服务端 | 确认服务端接收并处理目标 |
| 反馈（Feedback） | 服务端告诉客户端当前进度 | 服务端 → 客户端 | 执行过程中有实时反馈 |
| 结果（Result） | 服务端告诉客户端最终执行结果 | 服务端 → 客户端 | 任务结束后有明确结论 |

### 2.2 底层结构

一个 Action = 三个服务 + 两个话题。

**三个服务**

| 服务 | 作用 |
|------|------|
| 目标传递服务 | 客户端发目标给服务端 |
| 结果传递服务 | 服务端把最终结果给客户端 |
| 取消执行服务 | 客户端请求取消当前任务 |

**两个话题**

| 话题 | 方向 | 作用 |
|------|------|------|
| 反馈话题 | 服务端发布，客户端订阅 | 实时进度 |
| 状态话题 | 服务端发布，客户端订阅 | 当前任务状态 |

Action 不是一个全新的底层机制，它是用话题和服务拼出来的。ROS2 把它封装成一个 Action 接口，你只写一个 `.action` 文件，ROS2 自动生成对应的服务和话题。

### 2.3 接口文件格式

`.action` 文件用 `---` 分成三段，顺序固定：

```
# Goal
float32 distance
---
# Result
float32 pose
---
# Feedback
float32 pose
uint32 status
```

第一段是目标，第二段是结果，第三段是反馈。不能颠倒。

### 2.4 常量名注意

教材里写的是 `STATUS_MOVEING`（多了个 E），这是拼写错误。正确的英文是 `STATUS_MOVING`。接口文件和代码里都要用正确拼写，并且前后一致。

## 三、CLI 工具

### 3.1 `ros2 action list`

列出系统中所有 Action。

```bash
ros2 action list
ros2 action list -t
```

加 `-t` 显示类型。知道了类型，就可以用 `ros2 interface show` 看接口定义。

### 3.2 `ros2 action info`

查看某个 Action 的客户端和服务端信息。

```bash
ros2 action info /turtle1/rotate_absolute
```

输出告诉你：谁在发目标（客户端），谁在执行（服务端）。

### 3.3 `ros2 action send_goal`

从命令行发送一个目标。

```bash
ros2 action send_goal <action名> <action类型> "<目标YAML>"
```

目标 YAML 用 `{字段: 值}` 形式，冒号后必须有空格。

加 `--feedback` 参数，能看到执行过程中的实时反馈。不加的话只有 Goal 和 Result。

### 3.4 `ros2 interface show`

查看 Action 接口定义。

```bash
ros2 interface show turtlesim/action/RotateAbsolute
```

输出三段，分别对应 Goal、Result、Feedback。

## 四、Python 实现结构

### 4.1 文件分工

Python 版 Action 示例分为三个文件。

| 文件 | 角色 | 职责 |
|------|------|------|
| `robot.py` | 机器人类 | 纯逻辑，管理位置、状态、移动步骤 |
| `action_robot_02.py` | Action 服务端 | 接收目标、执行移动、发布反馈、发布结果、处理取消 |
| `action_control_02.py` | Action 客户端 | 发送目标、接收反馈、接收结果、发送取消 |

机器人类和服务端分离，是为了让机器人逻辑和通信逻辑解耦。机器人类只管“怎么动”，服务端只管“怎么和客户端通信”。

### 4.2 接口生成的文件

编译后，ROS2 根据 `.action` 文件生成 Python 模块，里面定义了三个类：

- `MoveRobot.Goal`
- `MoveRobot.Result`
- `MoveRobot.Feedback`

每个类对应 `.action` 文件里的一段。生成的文件在 `install/` 下，不在 `src/` 下。

## 五、Action 服务端

### 5.1 三个回调

| 回调 | 作用 | Python 默认行为 |
|------|------|-----------------|
| `execute_callback` | 执行目标 | 无默认，必须写 |
| `cancel_callback` | 处理取消请求 | 默认拒绝（`REJECT`） |
| `goal_callback` | 处理目标请求 | 默认接受（`ACCEPT`） |
| `handle_accepted_callback` | 目标被接受后做什么 | 默认立即执行 |

Python 只需要写 `execute_callback`。要支持取消，必须覆盖 `cancel_callback`。

这是 Python 比 C++ 简单的地方。C++ 里四个回调都要自己写，Python 有默认实现。

### 5.2 `goal_handle` 的常用方法和属性

| 方法/属性 | 作用 |
|-----------|------|
| `goal_handle.request` | 客户端发来的目标数据 |
| `goal_handle.publish_feedback(fb)` | 发布一条反馈 |
| `goal_handle.is_cancel_requested` | 是否被请求取消（属性，不加括号） |
| `goal_handle.succeed()` | 标记任务成功 |
| `goal_handle.canceled()` | 标记任务被取消 |
| `goal_handle.abort()` | 标记任务失败 |

### 5.3 返回值的含义

`execute_callback` 的返回值就是 Action 的最终结果。返回后，ROS2 通过结果服务把它发给客户端。

- 正常完成：先 `goal_handle.succeed()`，再 `return result`
- 被取消：不调用 `succeed()`，直接 `return result`（可配合 `goal_handle.canceled()`）

客户端收到结果时，能通过状态区分：

- `SUCCEEDED`：正常完成
- `CANCELED`：被取消
- `ABORTED`：执行失败

### 5.4 必须用多线程执行器

服务端的 `execute_callback` 里通常有一个长时间运行的 while 循环。如果用单线程执行器（`rclpy.spin`），这个循环会占满唯一的线程，取消回调、反馈发布都会被阻塞，取消功能无法生效。

必须用 `MultiThreadedExecutor`：

- `execute_callback` 在一个线程里跑循环
- `cancel_callback` 在另一个线程里被调用
- 两者不互相阻塞

这是 Action 服务端的一个工程要点。教材简化示例时把多线程执行器注释掉了，但对取消流程来说，这个简化会导致功能失效。

## 六、Action 客户端

### 6.1 三个回调

| 回调 | 触发时机 |
|------|----------|
| `goal_response_callback` | 服务端响应目标后，接受或拒绝 |
| `feedback_callback` | 服务端发布反馈时 |
| `get_result_callback` | 服务端发布结果时 |

### 6.2 执行顺序

正常执行时：

1. 客户端发送目标
2. 服务端响应：接受或拒绝
3. 如果接受，服务端开始执行
4. 执行过程中，多次触发 `feedback_callback`
5. 执行完成，触发 `get_result_callback`

如果被拒绝，只有第 2 步，后面两个回调都不会触发。

### 6.3 异步机制

客户端的发送、等待结果都是异步的，通过 future 机制实现。

- `send_goal_async` 返回一个 future，代表“发送操作的未来结果”
- 在 future 上调用 `add_done_callback` 注册回调，future 完成时通知
- `get_result_async` 同样返回 future

future 必须存成属性（`self._send_goal_future = ...`），否则：

- 无法注册后续回调
- future 可能被垃圾回收，异步操作行为不保证

这是 ROS2 Python 编程的通用规则：**创建的通信对象和 future 都要存成属性，避免被回收**。

### 6.4 取消功能

取消请求发给的是目标，不是 future。所以必须把 `goal_handle` 存成属性，在需要时调 `cancel_goal_async()`。

### 6.5 取消定时器的时序

如果取消定时器在 `__init__` 里创建，可能在目标被接受前就触发，此时 `goal_handle` 还是 `None`，取消请求发不出去。

正确做法：在 `goal_response_callback` 里，确认目标被接受后，再创建取消定时器。

原因：`send_goal` 里通常有 `wait_for_server()`，会阻塞执行器。如果服务端上线花很久，`send_goal` 一直卡着，执行器不能处理其他回调。取消定时器到期后排队等待，等 `send_goal` 一让出执行器，取消回调就立刻触发，此时 `goal_response_callback` 还没执行。

## 七、取消功能的完整链路

| 步骤 | 客户端 | 服务端 |
|------|--------|--------|
| 1 | 发目标 | 收到目标 |
| 2 | 收到目标接受响应，保存 `goal_handle` | 执行 `execute_callback` |
| 3 | 创建取消定时器 | 循环移动，发布反馈 |
| 4 | 定时器触发，调 `cancel_goal_async()` | 收到取消，`cancel_callback` 返回 ACCEPT |
| 5 | 等待结果 | 检测 `is_cancel_requested`，`stop_move`，`canceled()`，返回结果 |
| 6 | 收到 CANCELED 状态和最终位置 | 退出循环 |

## 八、取消功能失效的两个叠加原因

取消功能容易卡住，通常不是单一原因，而是两个问题叠加。

### 8.1 客户端的时序问题

取消定时器在 `__init__` 里创建，可能在目标被接受前触发。此时 `_goal_handle` 是 `None`，取消请求根本没发出去。

解决：把取消定时器的创建移到 `goal_response_callback` 里。

### 8.2 服务端的执行器问题

服务端用单线程执行器，`execute_callback` 的 while 循环占满线程，取消回调排队等不到执行。

解决：换 `MultiThreadedExecutor`。

单独解决任何一个都不够。两个都修了，取消才能生效。

## 九、Python 版比 C++ 版简单在哪

| 项目 | C++ | Python |
|------|-----|--------|
| 回调数量 | 要写 handle_goal、handle_cancel、handle_accepted、execute_move 四个 | 只写一个 execute_callback，其他用默认 |
| 线程 | 要开 std::thread 避免阻塞 | 用 time.sleep 就够，或加多线程执行器 |
| 客户端回调 | 用 std::bind 绑定 | 直接写方法，用 add_done_callback |
| 代码量 | 多 | 少 |

Python 的默认回调帮了大忙。只有需要拒绝某些目标、或者允许取消时，才需要覆盖默认行为。

## 十、Action 与其他通信方式对比

| 通信方式 | 模型 | 适用场景 | 反馈 | 取消 |
|----------|------|----------|------|------|
| 话题 | 发布/订阅 | 持续数据流 | 无 | 不适用 |
| 服务 | 请求/响应 | 短任务、查询 | 无 | 无 |
| 参数 | 键值配置 | 节点设置 | 无 | 不适用 |
| 动作 | 目标/反馈/结果 | 长任务 | 有 | 有 |

一句话区分：

- 持续流动的数据用话题
- 一次性的请求响应用服务
- 配置值用参数
- 需要过程反馈、可能中途取消的长任务用动作
