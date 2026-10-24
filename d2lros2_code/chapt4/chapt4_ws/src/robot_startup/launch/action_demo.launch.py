from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    robot = Node(
        package= "example_action_rclpy",
        executable= "action_robot_02",
        output ="screen"
    )

    control = Node(
        package= "example_action_rclpy",
        executable="action_control_02",
        output = "screen"
    )

    return LaunchDescription([robot,control])