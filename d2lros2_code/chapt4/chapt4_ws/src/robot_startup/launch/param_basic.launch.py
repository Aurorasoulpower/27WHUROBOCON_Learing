from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    param_node = Node(
        package = "example_param_rclpy",
        executable="param_basic",
        output ="screen"
    )
    return LaunchDescription([param_node])