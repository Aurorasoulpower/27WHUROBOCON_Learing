---
created: 2026-10-03
type: 速查
tags:
  - "#ros2"
  - "#Python"
  - 速查
---
# 话题
## 发布者
```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class ParamPublisher(Node):
    def __init__(self):
        # 节点名直接写死（实际工程中节点名通常固定）
        super().__init__('param_publisher_node')

        # 1. 声明参数并直接给默认值（写法A核心）
        self.declare_parameter('topic_name', '/lab1/publisher_topic')
        self.declare_parameter('timer_period', 0.5)
        self.declare_parameter('qos_depth', 10)
        self.declare_parameter('payload_content', 'hello_ros2')

        # 2. 获取参数最终值（注意 .value）
        self.topic_name = self.get_parameter('topic_name').value
        self.timer_period = self.get_parameter('timer_period').value
        self.qos_depth = self.get_parameter('qos_depth').value
        self.payload = self.get_parameter('payload_content').value

        # 3. 显式配置 QoS（方便日后弱网调试丢包问题）
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=self.qos_depth
        )

        # 4. 创建发布者与定时器
        self.publisher_ = self.create_publisher(String, self.topic_name, qos_profile)
        self.timer_ = self.create_timer(self.timer_period, self.timer_callback)
        
        self.count = 0
        self.get_logger().info(f'发布者已启动 | 话题: {self.topic_name} | 周期: {self.timer_period}s')

    def timer_callback(self):
        msg = String()
        # 业务逻辑：组装消息
        msg.data = f'{self.payload} | 计数: {self.count}'
        
        self.publisher_.publish(msg)
        self.get_logger().info(f'发布: {msg.data}')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = ParamPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass # 捕获 Ctrl+C，不抛出异常
    finally:
        # 工程规范：确保资源被释放
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
```
## 订阅者
```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class ParamSubscriber(Node):
    def __init__(self):
        # 节点名直接写死
        super().__init__('param_subscriber_node')

        # 1. 声明参数并给默认值（注意：话题名默认值应与发布者保持一致）
        self.declare_parameter('topic_name', '/lab1/publisher_topic')
        self.declare_parameter('qos_depth', 10)

        # 2. 获取参数
        self.topic_name = self.get_parameter('topic_name').value
        self.qos_depth = self.get_parameter('qos_depth').value

        # 3. 显式配置 QoS（必须与发布者的 QoS 兼容，否则连不上）
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=self.qos_depth
        )

        # 4. 创建订阅者
        self.subscription_ = self.create_subscription(
            String,
            self.topic_name,
            self.topic_callback,
            qos_profile
        )
        self.get_logger().info(f'订阅者已启动 | 等待话题: {self.topic_name} 的消息...')

    def topic_callback(self, msg):
        # 业务逻辑：处理收到的数据
        self.get_logger().info(f'收到原始数据: {msg.data}')
        
        # 示例解析逻辑（按实际业务需求改写）
        if 'hello_ros2' in msg.data:
            self.get_logger().info('验证通过：收到有效指令')

def main(args=None):
    rclpy.init(args=args)
    node = ParamSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
```
## setup.py声明
```python
# 在 src/<包名>/setup.py 中找到 entry_points，按以下格式填空：
    entry_points={
        'console_scripts': [
            # 格式："可执行文件名 = 包名.文件名:main"
            "<可执行文件名> = <包名>.<节点脚本名>:main",
            # 示例："topic_publisher_02 = example_topic_rclpy.topic_publisher_02:main",
        ],
    },
```
## 编译运行
```python
# ================= 1. 编译与激活 =================
cd <工作空间根目录>
# 推荐加上 --symlink-install，以后改纯 Python 逻辑就不用反复编译了
colcon build --symlink-install --packages-select <包名>
# 每开新终端必须激活环境
source install/setup.bash

# ================= 2. 运行节点 =================
# 基础运行
ros2 run <包名> <可执行文件名>
# 运行时动态改参数（覆盖代码里的默认值）
ros2 run <包名> <可执行文件名> --ros-args -p topic_name:="<新话题名>" -p timer_period:=<新周期秒数>

# ================= 3. 常用调试命令 =================
# ros2 node list        # 查看所有运行中的节点
# ros2 topic list       # 查看所有活跃话题
# ros2 topic echo /话题 # 实时打印话题数据
# ros2 param list       # 查看节点声明的参数
# rqt                   # 打开图形化调试工具
```

# 服务

## 服务端

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class ParamServiceServer(Node):
    def __init__(self):
        # 节点名直接写死（实际工程中节点名通常固定）
        super().__init__('param_service_server_node')

        # 1. 声明参数并直接给默认值
        self.declare_parameter('service_name', '/lab2/add_two_ints')
        self.declare_parameter('log_level', 'info')

        # 2. 获取参数最终值（注意 .value）
        self.service_name = self.get_parameter('service_name').value
        self.log_level = self.get_parameter('log_level').value

        # 3. 创建服务端
        self.server_ = self.create_service(
            AddTwoInts,
            self.service_name,
            self.handle_add_two_ints
        )
        self.get_logger().info(f'服务端已启动 | 服务名: {self.service_name}')

    def handle_add_two_ints(self, request, response):
        # 业务逻辑：处理请求，填充响应
        self.get_logger().info(f'收到请求: a={request.a}, b={request.b}')
        response.sum = request.a + request.b
        self.get_logger().info(f'返回结果: sum={response.sum}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ParamServiceServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass  # 捕获 Ctrl+C，不抛出异常
    finally:
        # 工程规范：确保资源被释放
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## 客户端

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class ParamServiceClient(Node):
    def __init__(self):
        # 节点名直接写死
        super().__init__('param_service_client_node')

        # 1. 声明参数并给默认值（服务名默认值应与服务端保持一致）
        self.declare_parameter('service_name', '/lab2/add_two_ints')
        self.declare_parameter('request_a', 3)
        self.declare_parameter('request_b', 5)
        self.declare_parameter('wait_timeout', 1.0)

        # 2. 获取参数
        self.service_name = self.get_parameter('service_name').value
        self.request_a = self.get_parameter('request_a').value
        self.request_b = self.get_parameter('request_b').value
        self.wait_timeout = self.get_parameter('wait_timeout').value

        # 3. 创建客户端
        self.client_ = self.create_client(AddTwoInts, self.service_name)
        self.get_logger().info(f'客户端已启动 | 等待服务: {self.service_name}')

    def result_callback_(self, result_future):
        # 业务逻辑：处理响应
        response = result_future.result()
        self.get_logger().info(f'收到返回结果: sum={response.sum}')

    def send_request(self):
        # 等待服务端上线
        while rclpy.ok() and not self.client_.wait_for_service(timeout_sec=self.wait_timeout):
            self.get_logger().info('等待服务端上线...')

        # 构造请求
        request = AddTwoInts.Request()
        request.a = self.request_a
        request.b = self.request_b

        self.get_logger().info(f'发送请求: a={request.a}, b={request.b}')
        # 异步发送，注册回调
        self.client_.call_async(request).add_done_callback(self.result_callback_)


def main(args=None):
    rclpy.init(args=args)
    node = ParamServiceClient()
    try:
        node.send_request()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## setup.py 声明

```python
# 在 src/<包名>/setup.py 中找到 entry_points，按以下格式填空：
    entry_points={
        'console_scripts': [
            # 格式："可执行文件名 = 包名.文件名:main"
            "<可执行文件名> = <包名>.<节点脚本名>:main",
            # 示例：
            # "service_server_02 = example_service_rclpy.service_server_02:main",
            # "service_client_02 = example_service_rclpy.service_client_02:main",
        ],
    },
```

## 编译运行

```python
# ================= 1. 编译与激活 =================
cd <工作空间根目录>
# 推荐加上 --symlink-install，以后改纯 Python 逻辑就不用反复编译了
colcon build --symlink-install --packages-select <包名>
# 每开新终端必须激活环境
source install/setup.bash

# ================= 2. 运行节点 =================
# 终端 1：启动服务端
ros2 run <包名> <服务端可执行文件名>
# 终端 2：启动客户端
ros2 run <包名> <客户端可执行文件名>

# 运行时动态改参数（覆盖代码里的默认值）
ros2 run <包名> <服务端可执行文件名> --ros-args -p service_name:="<新服务名>"
ros2 run <包名> <客户端可执行文件名> --ros-args -p service_name:="<新服务名>" -p request_a:=10 -p request_b:=20

# ================= 3. 常用调试命令 =================
# ros2 node list                                # 查看所有运行中的节点
# ros2 service list                             # 查看所有活跃服务
# ros2 service type /服务名                      # 查看服务类型
# ros2 interface show <服务接口>                 # 查看服务接口定义
# ros2 service call /服务名 <服务接口> "{...}"   # 手动调用服务
# ros2 param list                               # 查看节点声明的参数
# rqt                                           # 打开图形化调试工具
```

# 参数
```python
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult


￼class ParamNode(Node):
    ￼def ￼￼init￼￼(self, name):
        super().￼￼init￼￼(name)

        # 1. 声明参数
        self.declare_parameter('param_name', default_value)

        # 2. 注册参数回调
        self.add_on_set_parameters_callback(self.param_callback)

        # 3. 启动时应用一次初始值
        self.apply_param(self.get_parameter('param_name').value)

    ￼def param_callback(self, params):
        """参数被设置前触发"""
        ￼for p in params:
            ￼if p.name == 'param_name':
                self.apply_param(p.value)
        return SetParametersResult(successful=True)

    ￼def apply_param(self, value):
        """公共逻辑：读参数后要做什么，统一写在这里"""
        # 使用 value 做具体的事
        ...


￼def main(args=None):
    rclpy.init(args=args)
    node = ParamNode("param_node")
    rclpy.spin(node)
    rclpy.shutdown()


￼if ￼￼name￼￼ == '￼￼main￼￼':
    main()
```

# 动作
## 服务端
```python
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.executors import MultiThreadedExecutor
from your_interfaces.action import YourAction


class YourActionServer(Node):
    def __init__(self, name):
        super().__init__(name)
        self.get_logger().info(f"节点已启动：{name}")

        self.action_server_ = ActionServer(
            self,
            YourAction,
            'your_action_name',             # ← 服务端和客户端必须一致
            self.execute_callback,
            cancel_callback=self.cancel_callback   # ← 支持取消必须传
        )

    def cancel_callback(self, goal_handle):
        """收到取消请求时触发，返回 ACCEPT 才生效"""
        self.get_logger().info("收到取消请求")
        # 可在这里做清理工作
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle: ServerGoalHandle):
        """目标被接受后执行，必须返回 Result"""
        self.get_logger().info("开始执行")

        # 构造反馈消息
        feedback_msg = YourAction.Feedback()

        while rclpy.ok():
            # 1. 执行一步
            ...

            # 2. 填充反馈
            feedback_msg.xxx = ...
            goal_handle.publish_feedback(feedback_msg)

            # 3. 检测取消
            if goal_handle.is_cancel_requested:
                result = YourAction.Result()
                result.xxx = ...
                goal_handle.canceled()
                self.get_logger().info("目标取消")
                return result

            # 4. 检测完成
            if 完成条件:
                break

            time.sleep(0.5)   # 不要用 create_rate，单线程执行器会死锁

        # 5. 正常完成
        goal_handle.succeed()
        result = YourAction.Result()
        result.xxx = ...
        return result


def main(args=None):
    rclpy.init(args=args)
    node = YourActionServer("your_server")
    executor = MultiThreadedExecutor()      # ← 必须用多线程执行器
    executor.add_node(node)
    executor.spin()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## 客户端

```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient, GoalStatus
from your_interfaces.action import YourAction


class YourActionClient(Node):
    def __init__(self, name):
        super().__init__(name)
        self.get_logger().info(f"节点已启动：{name}")

        self._goal_handle = None
        self._cancel_timer = None

        self.action_client_ = ActionClient(self, YourAction, 'your_action_name')
        self.send_goal_timer_ = self.create_timer(1, self.send_goal)

    def send_goal(self):
        """只发一次目标，发完取消自己的定时器"""
        self.send_goal_timer_.cancel()

        goal_msg = YourAction.Goal()
        goal_msg.xxx = ...                       # ← 设置目标字段

        self.action_client_.wait_for_server()

        self._send_goal_future = self.action_client_.send_goal_async(
            goal_msg, self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """服务端对目标的响应"""
        goal_handle = future.result()
        if not goal_handle.accepted:             # ← 注意：是属性，不加括号
            self.get_logger().info("目标被拒绝")
            return
        self.get_logger().info("目标被接受")

        self._goal_handle = goal_handle          # ← 存成属性，取消要用

        # 目标被接受后，再启动取消定时器
        self._cancel_timer = self.create_timer(3, self.cancel_goal)

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def cancel_goal(self):
        """发取消请求"""
        self._cancel_timer.cancel()
        if self._goal_handle is None:
            return
        self.get_logger().info("请求取消目标")
        self._goal_handle.cancel_goal_async()

    def get_result_callback(self, future):
        """最终结果"""
        result = future.result().result
        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"目标完成，结果 {result.xxx}")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(f"目标被取消，结果 {result.xxx}")
        else:
            self.get_logger().info(f"状态 {status}")

    def feedback_callback(self, feedback_msg):
        """执行过程中的反馈"""
        feedback = feedback_msg.feedback
        self.get_logger().info(f"反馈 {feedback.xxx}")


def main(args=None):
    rclpy.init(args=args)
    node = YourActionClient("your_client")
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## 接口包

### 2.1 `action/YourAction.action`

```
# Goal
<字段定义>
---
# Result
<字段定义>
---
# Feedback
<字段定义>
```

三段顺序固定：Goal、Result、Feedback。

### 2.2 `package.xml` 需加

```xml
<depend>rosidl_default_generators</depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 2.3 `CMakeLists.txt` 需加

```cmake
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/YourAction.action"
)

ament_export_dependencies(rosidl_default_runtime)
```

### 2.4 编译接口包

```bash
colcon build --packages-select your_interfaces
source install/setup.bash
```

---

## 功能包

```bash
ros2 pkg create your_action_pkg \
  --build-type ament_python \
  --dependencies rclpy your_interfaces \
  --destination-directory src \
  --node-name your_server \
  --maintainer-name "your_name" \
  --maintainer-email "your@email.com"
```


| 文件 | 要加什么 |
|------|----------|
| `setup.py` | `entry_points` 里注册服务端和客户端两个入口 |

```python
entry_points={
    'console_scripts': [
        'your_server = your_action_pkg.your_server:main',
        'your_client = your_action_pkg.your_client:main',
    ],
},
```

| 文件 | 要加什么 |
|------|----------|
| `package.xml` | 确保有 `<depend>rclpy</depend>` 和 `<depend>your_interfaces</depend>` |
## 编译运行

###  编译

```bash
cd your_ws

# 先编译接口包
colcon build --packages-select your_interfaces
source install/setup.bash

# 再编译功能包
colcon build --packages-select your_action_pkg
source install/setup.bash
```

或者一步到位：

```bash
colcon build --packages-up-to your_action_pkg
source install/setup.bash
```

###  运行

终端一（服务端）：

```bash
source install/setup.bash
ros2 run your_action_pkg your_server
```

终端二（客户端）：

```bash
source install/setup.bash
ros2 run your_action_pkg your_client
```

### 7.3 验证

```bash
# 列出 Action
ros2 action list
ros2 action list -t

# 查看 Action 详情
ros2 action info /your_action_name

# 查看接口定义
ros2 interface show your_interfaces/action/YourAction

# 命令行发目标
ros2 action send_goal /your_action_name your_interfaces/action/YourAction "{xxx: 值}" --feedback
```

