import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class ServiceClient02(Node):
    def __init__(self, name):
        super().__init__(name)
        self.get_logger().info("节点已启动:%s!" % name)

        self.client_ = self.create_client(AddTwoInts, "add_two_ints_srv")

    def result_callback_(self, result_future):
        response = result_future.result()
        self.get_logger().info(f"收到返回结果：{response.sum}")

    def send_request(self, a, b):
        while rclpy.ok() and not self.client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("等待服务端上线……")

        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        #异步发送请求，不阻塞
        self.client_.call_async(request).add_done_callback(self.result_callback_)


def main(args=None):
    rclpy.init(args=args)
    node = ServiceClient02("service_client_02")
    node.send_request(3, 4)
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()