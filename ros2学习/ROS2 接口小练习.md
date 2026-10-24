# 一、整体目标

设计两个节点：

- **机器人节点** `example_interfaces_robot_02`：对外提供移动服务，发布机器人状态。
- **控制节点** `example_interfaces_control_02`：调用移动服务，订阅机器人状态。

通信方式：

| 通信 | 接口 | 方向 |
|---|---|---|
| 服务 | `MoveRobot.srv` | 控制节点 → 机器人节点 |
| 话题 | `RobotStatus.msg` | 机器人节点 → 控制节点 |

---

# 二、创建自定义接口功能包

## 2.1 进入工作空间 src

```bash
cd chapt3_ws/src
```

所有功能包统一创建在 `src` 下。

## 2.2 创建接口功能包

```bash
ros2 pkg create example_ros2_interfaces \
  --build-type ament_cmake \
  --dependencies rosidl_default_generators geometry_msgs
```

参数说明：

- `--build-type ament_cmake`：接口包必须是 `ament_cmake`。
- `rosidl_default_generators`：接口生成工具，必须依赖。
- `geometry_msgs`：接口里用到 `geometry_msgs/Pose` 时依赖。

---

# 三、编写接口文件

## 3.1 创建文件夹

```bash
cd example_ros2_interfaces
mkdir msg
mkdir srv
```

## 3.2 话题接口 `msg/RobotStatus.msg`

```text
uint32 STATUS_MOVING = 1
uint32 STATUS_STOP = 2
uint32 status
float32 pose
```

- `STATUS_MOVING = 1`：常量，移动中。
- `STATUS_STOP = 2`：常量，停止。
- `status`：当前状态。
- `pose`：当前位置，浮点数。

## 3.3 话题接口 `msg/RobotPose.msg`

```text
uint32 STATUS_MOVING = 1
uint32 STATUS_STOP = 2
uint32 status
geometry_msgs/Pose pose
```

和 `RobotStatus.msg` 的区别：

- `RobotStatus.msg` 用 `float32 pose`。
- `RobotPose.msg` 用 `geometry_msgs/Pose pose`。

这是为了演示基础类型和包装类型两种写法。实际项目按需选一种。

## 3.4 服务接口 `srv/MoveRobot.srv`

```text
# 前进后退的距离
float32 distance
---
# 当前的位置
float32 pose
```

- `---` 上面：请求字段 `distance`。
- `---` 下面：响应字段 `pose`。

---

# 四、修改接口包配置

## 4.1 修改 `CMakeLists.txt`

```cmake
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotPose.msg"
  "msg/RobotStatus.msg"
  "srv/MoveRobot.srv"
  DEPENDENCIES geometry_msgs
)
```

说明：

- `find_package(rosidl_default_generators REQUIRED)`：找到接口生成工具。
- `find_package(geometry_msgs REQUIRED)`：找到几何消息包。
- `rosidl_generate_interfaces`：注册所有接口文件。
- `DEPENDENCIES geometry_msgs`：因为 `RobotPose.msg` 里用了 `geometry_msgs/Pose`。

## 4.2 修改 `package.xml`

```xml
<buildtool_depend>ament_cmake</buildtool_depend>

<depend>rosidl_default_generators</depend>
<depend>geometry_msgs</depend>

<member_of_group>rosidl_interface_packages</member_of_group>
```

关键点：

- `<member_of_group>rosidl_interface_packages</member_of_group>`：必须手动加，声明这是接口包。

---

# 五、编译接口包

```bash
cd chapt3_ws
colcon build --packages-select example_ros2_interfaces
source install/setup.bash
```

编译后：

- C++ 头文件：`install/example_ros2_interfaces/include/`
- Python 文件：`install/example_ros2_interfaces/local/lib/python3.10/dist-packages/`

`source install/setup.bash` 把 `install` 目录加入环境变量，程序才能找到接口。

---

# 六、创建 Python 节点功能包

## 6.1 在 src 下创建

```bash
cd chapt3_ws/src
ros2 pkg create example_interfaces_rclpy \
  --build-type ament_python \
  --dependencies rclpy example_ros2_interfaces \
  --node-name example_interfaces_robot_02 \
  --maintainer-name "fishros" \
  --maintainer-email "fishros@foxmail.com"
```

## 6.2 手动创建控制节点文件

```bash
cd example_interfaces_rclpy/example_interfaces_rclpy
touch example_interfaces_control_02.py
```

## 6.3 修改 `setup.py`

```python
entry_points={
    'console_scripts': [
        'example_interfaces_robot_02 = example_interfaces_rclpy.example_interfaces_robot_02:main',
        'example_interfaces_control_02 = example_interfaces_rclpy.example_interfaces_control_02:main'
    ],
},
```

---

# 七、机器人节点源码

`example_interfaces_rclpy/example_interfaces_rclpy/example_interfaces_robot_02.py`

```python
import rclpy
from rclpy.node import Node
from example_ros2_interfaces.msg import RobotStatus
from example_ros2_interfaces.srv import MoveRobot
import math
from time import sleep


class Robot():
    def __init__(self) -> None:
        self.current_pose_ = 0.0
        self.target_pose_ = 0.0
        self.status_ = RobotStatus.STATUS_STOP

    def get_status(self):
        return self.status_

    def get_current_pose(self):
        return self.current_pose_

    def move_distance(self, distance):
        self.status_ = RobotStatus.STATUS_MOVING
        self.target_pose_ += distance

        while math.fabs(self.target_pose_ - self.current_pose_) > 0.01:
            step = distance / math.fabs(distance) * math.fabs(self.target_pose_ - self.current_pose_) * 0.1
            self.current_pose_ += step
            print(f"移动了：{step},当前位置为{self.current_pose_}")
            sleep(0.5)

        self.status_ = RobotStatus.STATUS_STOP
        return self.current_pose_


class ExampleInterfacesRobot02(Node):
    def __init__(self, name):
        super().__init__(name)
        self.get_logger().info("节点已启动：%s!" % name)
        self.robot = Robot()

        self.status_map_ = {
            RobotStatus.STATUS_MOVING: "移动中",
            RobotStatus.STATUS_STOP: "停止",
        }

        self.move_robot_server_ = self.create_service(
            MoveRobot, "move_robot", self.handle_move_robot
        )

        self.robot_status_publisher_ = self.create_publisher(
            RobotStatus, "robot_status", 10
        )

        self.publisher_timer_ = self.create_timer(
            0.5, self.publisher_timer_callback
        )

    def publisher_timer_callback(self):
        msg = RobotStatus()
        msg.status = self.robot.get_status()
        msg.pose = self.robot.get_current_pose()
        self.robot_status_publisher_.publish(msg)

        status_text = self.status_map_.get(msg.status, "未知")
        self.get_logger().info(f"当前状态：{status_text} 位置：{msg.pose}")

    def handle_move_robot(self, request, response):
        self.robot.move_distance(request.distance)
        response.pose = self.robot.get_current_pose()
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ExampleInterfacesRobot02("example_interfaces_robot_02")
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 八、控制节点源码

`example_interfaces_rclpy/example_interfaces_rclpy/example_interfaces_control_02.py`

```python
import rclpy
from rclpy.node import Node
from example_ros2_interfaces.msg import RobotStatus
from example_ros2_interfaces.srv import MoveRobot


class ExampleInterfacesControl02(Node):
    def __init__(self, name):
        super().__init__(name)
        self.get_logger().info("节点已启动：%s!" % name)

        self.status_map_ = {
            RobotStatus.STATUS_MOVING: "移动中",
            RobotStatus.STATUS_STOP: "停止",
        }

        self.client_ = self.create_client(MoveRobot, "move_robot")

        self.robot_status_subscribe_ = self.create_subscription(
            RobotStatus,
            "robot_status",
            self.robot_status_callback,
            10
        )

    def robot_status_callback(self, msg):
        status_text = self.status_map_.get(msg.status, "未知")
        self.get_logger().info(f"收到状态数据 位置：{msg.pose} 状态：{status_text}")

    def move_result_callback_(self, result_future):
        response = result_future.result()
        self.get_logger().info(f"收到返回结果：{response.pose}")

    def move_robot(self, distance):
        while rclpy.ok() and not self.client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("等候服务端上线……")

        request = MoveRobot.Request()
        request.distance = distance
        self.get_logger().info(f"请求服务让机器人移动{distance}")

        self.client_.call_async(request).add_done_callback(self.move_result_callback_)


def main(args=None):
    rclpy.init(args=args)
    node = ExampleInterfacesControl02("example_interfaces_control_02")
    node.move_robot(5.0)
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

# 九、编译运行

## 9.1 编译

```bash
cd chapt3_ws
colcon build --packages-up-to example_interfaces_rclpy
source install/setup.bash
```

`--packages-up-to`：编译指定包及其依赖，会先编译 `example_ros2_interfaces`，再编译 `example_interfaces_rclpy`。

## 9.2 运行机器人节点

终端 1：

```bash
source install/setup.bash
ros2 run example_interfaces_rclpy example_interfaces_robot_02
```

## 9.3 运行控制节点

终端 2：

```bash
source install/setup.bash
ros2 run example_interfaces_rclpy example_interfaces_control_02
```

---

# 十、现象与已知问题

## 10.1 正常现象

- 控制节点发起服务请求，机器人开始移动。
- 机器人每 0.5 秒发布一次状态。
- 移动结束后，控制节点收到服务响应。

## 10.2 已知问题：移动期间收不到状态话题

原因：

- Python 节点默认单线程执行器。
- `handle_move_robot` 回调里调用 `move_distance`，内部有 `while` 循环和 `sleep(0.5)`，阻塞了主线程。
- 定时器回调 `publisher_timer_callback` 无法执行，状态话题发不出去。

解决方法（进阶篇）：

- 使用多线程执行器 `MultiThreadedExecutor`。
- 使用回调组 `ReentrantCallbackGroup`。
- 把耗时任务放到单独线程。
- 长任务改用动作 Action。

---

# 十一、易错点

## 11.1 接口相关

- 接口包必须是 `ament_cmake`，不能是 `ament_python`。
- `package.xml` 必须手动加 `<member_of_group>rosidl_interface_packages</member_of_group>`。
- `CMakeLists.txt` 必须用 `rosidl_generate_interfaces` 注册所有接口文件。
- 接口里用到 `geometry_msgs/Pose`，必须在 `CMakeLists.txt` 和 `package.xml` 都声明依赖。
- 接口常量名要和代码里用的完全一致，比如 `STATUS_MOVING` 和 `STATUS_MOVEING` 不能混。

## 11.2 节点相关

- `get_current_pose` 返回值属性名要和 `__init__` 里定义的一致。
- 定时器回调函数名要和 `create_timer` 里注册的名字一致。
- 服务端和客户端的服务名必须一致，都是 `"move_robot"`。
- 发布者和订阅者的话题名必须一致，都是 `"robot_status"`。
- 客户端 `wait_for_service` 前不要漏掉 `client_` 后面的 `.`。
- 请求代码要放在 `while` 外面，不要缩进到 `while` 里。
- 异步请求后，主函数里必须有 `rclpy.spin(node)`，否则回调不会执行。

## 11.3 环境相关

- 编译后必须 `source install/setup.bash`。
- 如果报 `PackageNotFoundError`，先清理再重建：

  ```bash
  rm -rf build install log
  colcon build
  source install/setup.bash
  ```

---

# 十二、常用命令速查

```bash
# 查看接口定义
ros2 interface show example_ros2_interfaces/msg/RobotStatus
ros2 interface show example_ros2_interfaces/srv/MoveRobot

# 查看服务列表
ros2 service list
ros2 service type /move_robot

# 手动调用服务
ros2 service call /move_robot example_ros2_interfaces/srv/MoveRobot "{distance: 5}"

# 查看话题列表
ros2 topic list -t
ros2 topic echo /robot_status

# 查看话题频率
ros2 topic hz /robot_status
```

---