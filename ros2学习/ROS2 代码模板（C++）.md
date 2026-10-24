---
created: 2026-10-03
type: 速查
tags:
  - "#ros2"
  - "#cpp"
  - 速查
---
# 话题
## 发布者
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "rclcpp/qos.hpp" // 用于显式配置 QoS

class ParamPublisher : public rclcpp::Node
{
public:
    ParamPublisher() : Node("param_publisher_node")
    {
        // 1. 声明参数 (写法A：直接在此给默认值，支持运行命令行覆盖)
        this->declare_parameter<std::string>("topic_name", "/lab1/publisher_topic");
        this->declare_parameter<double>("timer_period", 0.5);
        this->declare_parameter<int>("qos_depth", 10);
        this->declare_parameter<std::string>("payload_content", "hello_ros2");

        // 2. 获取最终生效的参数值（注意 C++ 需指定类型 as_xxx）
        std::string topic_name = this->get_parameter("topic_name").as_string();
        double timer_period = this->get_parameter("timer_period").as_double();
        int qos_depth = this->get_parameter("qos_depth").as_int();
        payload_ = this->get_parameter("payload_content").as_string();

        // 3. 显式配置 QoS
        rclcpp::QoS qos_profile(rclcpp::KeepLast(qos_depth));
        qos_profile.reliable(); // 可靠传输

        // 4. 创建发布者与定时器
        publisher_ = this->create_publisher<std_msgs::msg::String>(topic_name, qos_profile);
        
        // 使用 std::bind 绑定回调函数
        timer_ = this->create_wall_timer(
            std::chrono::duration<double>(timer_period),
            std::bind(&ParamPublisher::timer_callback, this));

        count_ = 0;
        RCLCPP_INFO(this->get_logger(), "发布者已启动 | 话题: %s | 周期: %.2fs", 
                    topic_name.c_str(), timer_period);
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = payload_ + " | 计数: " + std::to_string(count_);
        
        publisher_->publish(message);
        RCLCPP_INFO(this->get_logger(), "发布: %s", message.data.c_str());
        count_++;
    }

    // 成员变量声明（统一使用智能指针 SharedPtr）
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    std::string payload_;
    int count_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ParamPublisher>();
    
    try {
        rclcpp::spin(node);
    } catch (const std::exception &e) {
        RCLCPP_ERROR(node->get_logger(), "异常: %s", e.what());
    }
    
    rclcpp::shutdown();
    return 0;
}
```

## 订阅者
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "rclcpp/qos.hpp"

class ParamSubscriber : public rclcpp::Node
{
public:
    ParamSubscriber() : Node("param_subscriber_node")
    {
        // 1. 声明参数（默认值需与发布者保持一致）
        this->declare_parameter<std::string>("topic_name", "/lab1/publisher_topic");
        this->declare_parameter<int>("qos_depth", 10);

        // 2. 获取参数
        std::string topic_name = this->get_parameter("topic_name").as_string();
        int qos_depth = this->get_parameter("qos_depth").as_int();

        // 3. 显式配置 QoS
        rclcpp::QoS qos_profile(rclcpp::KeepLast(qos_depth));
        qos_profile.reliable();

        // 4. 创建订阅者
        // 注意占位符 std::placeholders::_1，表示接收的消息作为第一个参数传给回调
        subscription_ = this->create_subscription<std_msgs::msg::String>(
            topic_name, qos_profile,
            std::bind(&ParamSubscriber::topic_callback, this, std::placeholders::_1));

        RCLCPP_INFO(this->get_logger(), "订阅者已启动 | 等待话题: %s 的消息...", topic_name.c_str());
    }

private:
    // 回调参数使用 SharedPtr 避免大对象拷贝
    void topic_callback(const std_msgs::msg::String::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "收到原始数据: %s", msg->data.c_str());
        
        // 业务逻辑解析
        if (msg->data.find("hello_ros2") != std::string::npos) {
            RCLCPP_INFO(this->get_logger(), "验证通过：收到有效指令");
        }
    }

    // 成员变量
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ParamSubscriber>();
    
    try {
        rclcpp::spin(node);
    } catch (const std::exception &e) {
        RCLCPP_ERROR(node->get_logger(), "异常: %s", e.what());
    }
    
    rclcpp::shutdown();
    return 0;
}
```

## CMake配置
```cmake
# 1. 寻找依赖
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# 2. 编译发布者
add_executable(param_publisher src/param_publisher.cpp)
ament_target_dependencies(param_publisher rclcpp std_msgs)

# 3. 编译订阅者
add_executable(param_subscriber src/param_subscriber.cpp)
ament_target_dependencies(param_subscriber rclcpp std_msgs)

# 4. 安装（相当于 Python 的 entry_points）
install(TARGETS
  param_publisher
  param_subscriber
  DESTINATION lib/${PROJECT_NAME}
)
```

## 编译运行
```bash
# ================= 1. 编译与激活 =================
cd <工作空间根目录>
colcon build --packages-select <包名>
source install/setup.bash

# ================= 2. 运行节点 =================
# 终端1：发布者
ros2 run <包名> param_publisher
# 终端2：订阅者
ros2 run <包名> param_subscriber

# ================= 3. 运行时动态改参 =================
# 直接命令行覆盖代码里的默认值（比如改成0.1秒周期，改成/robot1/cmd话题）
ros2 run <包名> param_publisher --ros-args \
  -p topic_name:="/robot1/cmd" \
  -p timer_period:=0.1 \
  -p payload_content:="fast_forward"

# ================= 4. 常用调试命令 =================
# ros2 node list
# ros2 topic list
# ros2 topic echo /robot1/cmd
# ros2 param list
# rqt
```

# 服务

## 服务端

```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

class ParamServiceServer : public rclcpp::Node
{
public:
    ParamServiceServer() : Node("param_service_server_node")
    {
        // 1. 声明参数 (写法A：直接在此给默认值，支持运行命令行覆盖)
        this->declare_parameter<std::string>("service_name", "/lab2/add_two_ints");

        // 2. 获取最终生效的参数值（注意 C++ 需指定类型 as_xxx）
        std::string service_name = this->get_parameter("service_name").as_string();

        // 3. 创建服务端
        // 使用 std::bind 绑定回调，占位符 _1 是请求，_2 是响应
        server_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            service_name,
            std::bind(&ParamServiceServer::handle_add_two_ints, this,
                      std::placeholders::_1, std::placeholders::_2));

        RCLCPP_INFO(this->get_logger(), "服务端已启动 | 服务名: %s", service_name.c_str());
    }

private:
    // 回调参数使用 SharedPtr，请求和响应都是共享指针
    void handle_add_two_ints(
        const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
        std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response)
    {
        // 业务逻辑：处理请求，填充响应
        RCLCPP_INFO(this->get_logger(), "收到请求: a=%ld, b=%ld", request->a, request->b);
        response->sum = request->a + request->b;
        RCLCPP_INFO(this->get_logger(), "返回结果: sum=%ld", response->sum);
        // 注意：不需要 return response，直接写入 response 即可
    }

    // 成员变量声明（统一使用智能指针 SharedPtr）
    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr server_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ParamServiceServer>();

    try {
        rclcpp::spin(node);
    } catch (const std::exception &e) {
        RCLCPP_ERROR(node->get_logger(), "异常: %s", e.what());
    }

    rclcpp::shutdown();
    return 0;
}
```

## 客户端

```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

class ParamServiceClient : public rclcpp::Node
{
public:
    ParamServiceClient() : Node("param_service_client_node")
    {
        // 1. 声明参数（服务名默认值需与服务端保持一致）
        this->declare_parameter<std::string>("service_name", "/lab2/add_two_ints");
        this->declare_parameter<int>("request_a", 3);
        this->declare_parameter<int>("request_b", 5);
        this->declare_parameter<double>("wait_timeout", 1.0);

        // 2. 获取参数
        service_name_ = this->get_parameter("service_name").as_string();
        request_a_ = this->get_parameter("request_a").as_int();
        request_b_ = this->get_parameter("request_b").as_int();
        wait_timeout_ = this->get_parameter("wait_timeout").as_double();

        // 3. 创建客户端
        client_ = this->create_client<example_interfaces::srv::AddTwoInts>(service_name_);
        RCLCPP_INFO(this->get_logger(), "客户端已启动 | 等待服务: %s", service_name_.c_str());
    }

    // 发送请求（主函数里调用）
    void send_request()
    {
        // 等待服务端上线
        while (rclcpp::ok() && !client_->wait_for_service(std::chrono::duration<double>(wait_timeout_))) {
            RCLCPP_INFO(this->get_logger(), "等待服务端上线...");
        }

        // 构造请求
        auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
        request->a = request_a_;
        request->b = request_b_;

        RCLCPP_INFO(this->get_logger(), "发送请求: a=%ld, b=%ld", request->a, request->b);

        // 异步发送，注册回调
        client_->async_send_request(
            request,
            std::bind(&ParamServiceClient::result_callback_, this,
                      std::placeholders::_1));
    }

private:
    // 响应回调：参数是 SharedFuture
    void result_callback_(
        rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedFuture result_future)
    {
        auto response = result_future.get();
        RCLCPP_INFO(this->get_logger(), "收到返回结果: sum=%ld", response->sum);
    }

    // 成员变量
    rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client_;
    std::string service_name_;
    int request_a_;
    int request_b_;
    double wait_timeout_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ParamServiceClient>();

    // 主动发起请求
    node->send_request();

    try {
        rclcpp::spin(node);
    } catch (const std::exception &e) {
        RCLCPP_ERROR(node->get_logger(), "异常: %s", e.what());
    }

    rclcpp::shutdown();
    return 0;
}
```

## CMake 配置

```cmake
# 1. 寻找依赖
find_package(rclcpp REQUIRED)
find_package(example_interfaces REQUIRED)

# 2. 编译服务端
add_executable(param_service_server src/param_service_server.cpp)
ament_target_dependencies(param_service_server rclcpp example_interfaces)

# 3. 编译客户端
add_executable(param_service_client src/param_service_client.cpp)
ament_target_dependencies(param_service_client rclcpp example_interfaces)

# 4. 安装（相当于 Python 的 entry_points）
install(TARGETS
  param_service_server
  param_service_client
  DESTINATION lib/${PROJECT_NAME}
)
```

## 编译运行

```bash
# ================= 1. 编译与激活 =================
cd <工作空间根目录>
colcon build --packages-select <包名>
source install/setup.bash

# ================= 2. 运行节点 =================
# 终端1：服务端
ros2 run <包名> param_service_server
# 终端2：客户端
ros2 run <包名> param_service_client

# ================= 3. 运行时动态改参 =================
# 服务端改服务名
ros2 run <包名> param_service_server --ros-args \
  -p service_name:="/robot1/add"

# 客户端改服务名和请求数值（和服务端保持一致才能连上）
ros2 run <包名> param_service_client --ros-args \
  -p service_name:="/robot1/add" \
  -p request_a:=10 \
  -p request_b:=20

# ================= 4. 常用调试命令 =================
# ros2 node list                                # 查看所有运行中的节点
# ros2 service list                             # 查看所有活跃服务
# ros2 service type /lab2/add_two_ints          # 查看服务类型
# ros2 interface show example_interfaces/srv/AddTwoInts   # 查看接口定义
# ros2 service call /lab2/add_two_ints example_interfaces/srv/AddTwoInts "{a: 10, b: 20}"   # 手动调用
# ros2 param list                               # 查看节点声明的参数
# rqt                                           # 打开图形化调试工具
```

