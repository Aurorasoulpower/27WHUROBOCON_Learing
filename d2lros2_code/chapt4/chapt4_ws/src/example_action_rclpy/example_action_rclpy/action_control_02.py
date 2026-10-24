import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from robot_control_interfaces.action import MoveRobot

class ActionControl02(Node):
    #客户端
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info("节点已启动%s!" % name)

        self._goal_handle = None
        self.cancel_timer_ = self.create_timer(5,self.cancel_goal)

        self.action_client_ = ActionClient(self,MoveRobot,'move_robot')

        self.send_goal_timer_ = self.create_timer(1,self.send_goal)

    def send_goal(self):
        self.send_goal_timer_.cancel()
        goal_msg = MoveRobot.Goal()
        goal_msg.distance = 5.0
        self.action_client_.wait_for_server()
        self._send_goal_future = self.action_client_.send_goal_async(goal_msg,self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self,future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info("目标被拒绝:(")
            return
        self.get_logger().info("目标被接受：）")

        self._goal_handle = goal_handle
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self,future):
        result = future.result().result
        status = future.result().status
        if status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info(f"目标被取消，当前位置 {result.pose}")
        elif status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"目标完成，当前位置 {result.pose}")
        else:
            self.get_logger().info(f"未知状态 {status}，位置 {result.pose}")

        

    def feedback_callback(self,feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"收到反馈是{feedback.pose}")

    def cancel_goal(self):
        self.cancel_timer_.cancel()

        if self._goal_handle is None:
            self.get_logger().info("还没有目标，无法取消")
            return
        self.get_logger().info("请求取消目标")
        self._goal_handle.cancel_goal_async()


def main(args=None):
    rclpy.init(args=args)
    node = ActionControl02("action_control_02")
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()