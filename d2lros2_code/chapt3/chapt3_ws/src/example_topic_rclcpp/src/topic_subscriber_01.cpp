#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class TopicSubscribe01:public rclcpp::Node
{
public:
    TopicSubscribe01(std::string name):Node(name)
    {
        RCLCPP_INFO(this->get_logger(),"大家好，我是%s.",name.c_str());
        command_subscribe_ = this->create_subscription<std_msgs::msg::String>(
            "command",10,
            std::bind(&TopicSubscribe01::command_callback,this,std::placeholders::_1));
    }
private:
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr command_subscribe_;
    void command_callback(const std_msgs::msg::String::SharedPtr msg)
    {
        double speed = 0.0;
        if (msg->data == "forward")
        {
            speed = 0.2;
        }
        RCLCPP_INFO(this->get_logger(),"收到[%s]指令，发送速度%f",msg->data.c_str(),speed);

    }

};

int main(int argc,char **argv)
{
    rclcpp::init(argc,argv);
    auto node = std::make_shared<TopicSubscribe01>("topic_subscriber_02");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}