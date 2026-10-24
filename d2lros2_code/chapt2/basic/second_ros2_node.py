import rclpy
from rclpy.node import Node 

rclpy.init()
rclpy.spin(Node("second_node"))