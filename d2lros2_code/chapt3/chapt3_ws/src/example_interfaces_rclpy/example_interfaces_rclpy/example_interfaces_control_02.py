import rclpy
from rclpy.node import Node
from example_ros2_interfaces.msg import RobotStatus
from example_ros2_interfaces.srv import MoveRobot

class ExampleInterfacesControl02(Node):
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info("节点已启动：%s!"%name)

        self.client_ = self.create_client(MoveRobot,"move_robot")

        self.robot_status_subscribe_ = self.create_subscription(RobotStatus,"robot_status",self.robot_status_callback,10)

    def robot_status_callback(self,msg):
        self.get_logger().info(f"收到状态数据位置：{msg.pose}状态{msg.status}")

    def move_result_callback_(self,result_future):
        response = result_future.result()
        self.get_logger().info(f"收到返回结果：{response.pose}")

    def move_robot(self,distance):
        while rclpy.ok() and not self.client_.wait_for_service(timeout_sec = 1.0):
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
