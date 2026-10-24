from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
     param1 = Node(
          package="example_param_rclpy",
          executable="param_basic",
          namespace="robot1",
          name="param_basic",
          parameters=[{'rcl_log_level':10}],
          output = "screen"
     )
     param2 = Node(
          package="example_param_rclpy",
          executable="param_basic",
          namespace="robot2",
          name="param_basic",
          parameters=[{'rcl_log_level':40}],
          output = "screen"
     )
     return LaunchDescription([param1, param2])