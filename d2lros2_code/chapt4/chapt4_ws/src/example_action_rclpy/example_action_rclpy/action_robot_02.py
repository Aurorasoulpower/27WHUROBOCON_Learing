import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.action import CancelResponse
from rclpy.action.server import ServerGoalHandle
from robot_control_interfaces.action import MoveRobot
from example_action_rclpy.robot import Robot
from rclpy.executors import MultiThreadedExecutor

class ActionRobot02(Node):
    #服务端
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info("节点已经启动%s!" % name)

        self.robot_ = Robot()
        self.action_server_ = ActionServer(self,MoveRobot,"move_robot",self.execute_callback,cancel_callback=self.cancel_callback)

    def cancel_callback(self,goal_handle):
        self.get_logger().info("收到取消请求，接受")
        return CancelResponse.ACCEPT
    
    def execute_callback(self,goal_handle:ServerGoalHandle):
        self.get_logger().info('执行移动机器人')
        feedback_msg = MoveRobot.Feedback()
        self.robot_.set_goal(goal_handle.request.distance)

        while rclpy.ok() and not self.robot_.close_goal():
            self.robot_.move_step()
            feedback_msg.pose = self.robot_.get_current_pose()
            feedback_msg.status = self.robot_.get_status()
            goal_handle.publish_feedback(feedback_msg)

            if goal_handle.is_cancel_requested:
                self.robot_.stop_move() 
                result = MoveRobot.Result()
                result.pose = self.robot_.get_current_pose()
                goal_handle.canceled()
                self.get_logger().info("目标取消")
                return result

            time.sleep(0.5)

        goal_handle.succeed()
        result = MoveRobot.Result()
        result.pose = self.robot_.get_current_pose()
        return result


def main(args=None):
    rclpy.init(args=args)
    node = ActionRobot02("action_robot_02")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
