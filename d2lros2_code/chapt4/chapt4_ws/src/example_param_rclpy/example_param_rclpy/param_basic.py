import rclpy
from rclpy.node import Node
from rclpy.logging import LoggingSeverity
from rcl_interfaces.msg import SetParametersResult

class ParamBasicNode(Node):
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info("节点已经启动：%s!"%name)

        self.declare_parameter('rcl_log_level',0)

        self.add_on_set_parameters_callback(self.param_callback)

        self.apply_log_level(self.get_parameter("rcl_log_level").value)

    def param_callback(self,params):
        for p in params:
            if p.name == 'rcl_log_level':
                self.apply_log_level(p.value)
                self.get_logger().info(f"日志级别已改成{p.value}")
        return SetParametersResult(successful=True)

    def apply_log_level(self,log_level):
        self.get_logger().set_level(LoggingSeverity(log_level))   

        print(f"========================{log_level}=============================")
        self.get_logger().debug("我是DEBUG级别的日志，我被打印出来了!")
        self.get_logger().info("我是INFO级别的日志，我被打印出来了!")
        self.get_logger().warn("我是WARN级别的日志，我被打印出来了!")
        self.get_logger().error("我是ERROR级别的日志，我被打印出来了!")
        self.get_logger().fatal("我是FATAL级别的日志，我被打印出来了!")

def main(args = None):
    rclpy.init(args=args)
    node = ParamBasicNode("param_basic")
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
