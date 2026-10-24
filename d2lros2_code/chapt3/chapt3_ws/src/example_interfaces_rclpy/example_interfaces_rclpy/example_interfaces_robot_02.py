import rclpy
from rclpy.node import Node
from example_ros2_interfaces.msg import RobotStatus
from example_ros2_interfaces.srv import MoveRobot
import math
from time import sleep


## 第一个类 机器人类
class Robot():
    def __init__(self)->None:
        self.current_pose_ = 0.0
        self.target_pose_ = 0.0
        self.status_ = RobotStatus.STATUS_STOP

    def get_status(self):
        return self.status_

    def get_current_pose(self):
        return self.current_pose_

    def move_distance(self,distance):
        self.status_ = RobotStatus.STATUS_MOVING
        self.target_pose_ += distance

        while math.fabs(self.target_pose_ - self.current_pose_)>0.01:
            step = distance / math.fabs(distance)* math.fabs(self.target_pose_-self.current_pose_)*0.1
            #计算公式，逐渐逼近，步长越来越小。前面部分 distance / math.fabs(distance) 仅取符号，后面为步长绝对值，剩余距离的1/10
            self.current_pose_ += step
            print(f"移动了：{step},当前位置为{self.current_pose_}")
            sleep(0.5)
        self.status_ = RobotStatus.STATUS_STOP
        return self.current_pose_

class ExampleInterfacesRobot02(Node):
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info("节点已启动：%s!"%name)
        self.robot =Robot()

        # 服务
        self.move_robot_server_ =self.create_service(MoveRobot,"move_robot",self.handle_move_robot)

        # 话题
        self.robot_status_publisher_ = self.create_publisher(RobotStatus,"robot_status",10)

        self.publisher_timer_ = self.create_timer(0.5,self.publisher_timer_callback)

    def publisher_timer_callback(self):
        msg = RobotStatus()
        msg.status = self.robot.get_status()
        msg.pose = self.robot.get_current_pose()
        self.robot_status_publisher_.publish(msg)
        self.get_logger().info(f"当前状态：{msg.status},位置:{msg.pose}")| NOTE: 状态 | File: VSCode代码记录 | ID: 1791115254 |

    def handle_move_robot(self,request,response):
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