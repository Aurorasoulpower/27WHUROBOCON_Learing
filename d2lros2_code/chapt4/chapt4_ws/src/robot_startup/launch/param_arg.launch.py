from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    ld.add_action(DeclareLaunchArgument(
        'log_level',
        default_value='20',
        description='日志级别：10=DEBUG 20=INFO 30=WARN 40=ERROR 50=FATAL'
    ))

    log_level_cfg = LaunchConfiguration('log_level')

    param_node = Node(
        package="example_param_rclpy",
        executable="param_basic",
        parameters=[{'rcl_log_level': log_level_cfg}],
        output="screen"
    )

    ld.add_action(param_node)

    return ld